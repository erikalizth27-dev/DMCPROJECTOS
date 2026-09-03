from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol

from siniestro_facil.domain.authorization import (
    Action,
    AlertDetailLevel,
    AuthorizationDenied,
    alert_detail_level,
    authorize,
)
from siniestro_facil.domain.fraud import (
    AlertEffect,
    AlertRecommendation,
    AlertReviewStatus,
    AlertSeverity,
)
from siniestro_facil.domain.idempotency import (
    fingerprint_request,
    validate_idempotency_key,
)
from siniestro_facil.domain.identity import AuthenticatedPrincipal
from siniestro_facil.infrastructure.fraud_adapter import FraudEvaluation


class FraudEvaluationError(RuntimeError):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


@dataclass(frozen=True, slots=True)
class EvaluateFraudCommand:
    claim_id: int
    facts: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class GeneratedAlert:
    id: int
    claim_id: int
    alert_type: str
    severity: AlertSeverity
    explanation: str
    source_data: dict[str, object]
    rule_or_model: str
    policy_version: str
    effect: AlertEffect
    review_status: AlertReviewStatus = AlertReviewStatus.PENDIENTE


@dataclass(frozen=True, slots=True)
class FraudEvaluationResult:
    claim_id: int
    alerts: tuple[GeneratedAlert, ...]


@dataclass(frozen=True, slots=True)
class StoredFraudRequest:
    fingerprint: str
    result: FraudEvaluationResult


@dataclass(frozen=True, slots=True)
class AlertView:
    id: int
    claim_id: int
    alert_type: str
    severity: AlertSeverity
    effect: AlertEffect
    review_status: AlertReviewStatus
    detail_level: AlertDetailLevel
    explanation: str | None
    source_data: dict[str, object] | None
    rule_or_model: str | None
    policy_version: str | None


class FraudRuleAdapter(Protocol):
    def evaluate(self, facts: Mapping[str, object]) -> FraudEvaluation: ...


class FraudAlertRepository(Protocol):
    def find_request(self, idempotency_key: str) -> StoredFraudRequest | None: ...

    def create(
        self,
        claim_id: int,
        evaluation: FraudEvaluation,
        principal: AuthenticatedPrincipal,
        *,
        idempotency_key: str,
        fingerprint: str,
    ) -> FraudEvaluationResult: ...

    def get_alert(self, claim_id: int, alert_id: int) -> GeneratedAlert | None: ...


class InMemoryFraudAlertRepository:
    def __init__(self) -> None:
        self._next_id = 1
        self._alerts: dict[int, GeneratedAlert] = {}
        self._requests: dict[str, StoredFraudRequest] = {}

    def find_request(self, idempotency_key: str) -> StoredFraudRequest | None:
        return self._requests.get(idempotency_key)

    def create(
        self,
        claim_id: int,
        evaluation: FraudEvaluation,
        principal: AuthenticatedPrincipal,
        *,
        idempotency_key: str,
        fingerprint: str,
    ) -> FraudEvaluationResult:
        generated: list[GeneratedAlert] = []
        for recommendation in evaluation.alerts:
            alert = GeneratedAlert(
                id=self._next_id,
                claim_id=claim_id,
                alert_type=recommendation.alert_type,
                severity=recommendation.severity,
                explanation=recommendation.explanation,
                source_data=recommendation.source_data,
                rule_or_model=recommendation.rule_or_model,
                policy_version=recommendation.policy_version,
                effect=recommendation.effect,
            )
            self._alerts[alert.id] = alert
            generated.append(alert)
            self._next_id += 1
        result = FraudEvaluationResult(claim_id, tuple(generated))
        self._requests[idempotency_key] = StoredFraudRequest(fingerprint, result)
        return result

    def get_alert(self, claim_id: int, alert_id: int) -> GeneratedAlert | None:
        alert = self._alerts.get(alert_id)
        return alert if alert is not None and alert.claim_id == claim_id else None


class EvaluateFraudService:
    def __init__(
        self,
        adapter: FraudRuleAdapter,
        repository: FraudAlertRepository,
    ) -> None:
        self._adapter = adapter
        self._repository = repository

    def execute(
        self,
        command: EvaluateFraudCommand,
        principal: AuthenticatedPrincipal,
        *,
        idempotency_key: str,
        request_payload: object,
    ) -> FraudEvaluationResult:
        try:
            authorize(
                principal.role,
                Action.REVISAR_ALERTA,
                resource_in_scope=True,
            )
        except AuthorizationDenied as exc:
            raise FraudEvaluationError(
                "FRAUD-EVALUATION-FORBIDDEN",
                "Acción no permitida para el rol",
                403,
            ) from exc
        if command.claim_id <= 0:
            raise FraudEvaluationError(
                "FRAUD-EVALUATION-INVALID",
                "El identificador del siniestro es inválido",
                422,
            )
        try:
            key = validate_idempotency_key(idempotency_key)
        except ValueError as exc:
            raise FraudEvaluationError(
                "IDEMPOTENCY-INVALID",
                str(exc),
                422,
            ) from exc
        fingerprint = fingerprint_request(request_payload)
        existing = self._repository.find_request(key)
        if existing is not None:
            if existing.fingerprint != fingerprint:
                raise FraudEvaluationError(
                    "IDEMPOTENCY-CONFLICT",
                    "Idempotency-Key ya fue utilizada con otro contenido",
                    409,
                )
            return existing.result
        evaluation = self._adapter.evaluate(command.facts)
        return self._repository.create(
            command.claim_id,
            evaluation,
            principal,
            idempotency_key=key,
            fingerprint=fingerprint,
        )


class GetFraudAlertService:
    def __init__(self, repository: FraudAlertRepository) -> None:
        self._repository = repository

    def execute(
        self,
        claim_id: int,
        alert_id: int,
        principal: AuthenticatedPrincipal,
    ) -> AlertView:
        try:
            level = alert_detail_level(principal.role)
        except AuthorizationDenied as exc:
            raise FraudEvaluationError(
                "ALERT-NOT-FOUND",
                "Alerta no encontrada",
                404,
            ) from exc
        alert = self._repository.get_alert(claim_id, alert_id)
        if alert is None:
            raise FraudEvaluationError(
                "ALERT-NOT-FOUND",
                "Alerta no encontrada",
                404,
            )
        detailed = level is AlertDetailLevel.DETALLE
        return AlertView(
            id=alert.id,
            claim_id=alert.claim_id,
            alert_type=alert.alert_type,
            severity=alert.severity,
            effect=alert.effect,
            review_status=alert.review_status,
            detail_level=level,
            explanation=alert.explanation if detailed else None,
            source_data=alert.source_data if detailed else None,
            rule_or_model=alert.rule_or_model if detailed else None,
            policy_version=alert.policy_version if detailed else None,
        )
