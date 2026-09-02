from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

from siniestro_facil.application.assistance_contracts import AssistanceRecord
from siniestro_facil.domain.assistance import AssistanceStatus
from siniestro_facil.domain.authorization import (
    Action,
    AuthorizationDenied,
    PrincipalRole,
    authorize,
)
from siniestro_facil.domain.idempotency import (
    fingerprint_request,
    validate_idempotency_key,
)
from siniestro_facil.domain.identity import AuthenticatedPrincipal
from siniestro_facil.infrastructure.provider_adapter import (
    ProviderAdapter,
    dispatch_assistance,
)


class AssistanceRequestError(RuntimeError):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


@dataclass(frozen=True, slots=True)
class RequestAssistanceCommand:
    claim_id: int
    provider_id: int
    assistance_type: str
    reason: str


@dataclass(frozen=True, slots=True)
class StoredAssistanceRequest:
    fingerprint: str
    result: AssistanceRecord


class RequestAssistanceRepository(Protocol):
    def find_request(
        self,
        idempotency_key: str,
        principal: AuthenticatedPrincipal,
    ) -> StoredAssistanceRequest | None: ...

    def create(
        self,
        command: RequestAssistanceCommand,
        principal: AuthenticatedPrincipal,
        *,
        idempotency_key: str,
        fingerprint: str,
    ) -> AssistanceRecord: ...

    def mark_sent(
        self,
        assistance_id: int,
        external_reference: str,
        principal: AuthenticatedPrincipal,
    ) -> AssistanceRecord: ...

    def get(
        self,
        claim_id: int,
        assistance_id: int,
        principal: AuthenticatedPrincipal,
    ) -> AssistanceRecord | None: ...


class InMemoryAssistanceRepository:
    def __init__(self, *, visible_claim_ids: set[int] | None = None) -> None:
        self._visible = set(visible_claim_ids or set())
        self._records: dict[int, AssistanceRecord] = {}
        self._requests: dict[str, StoredAssistanceRequest] = {}
        self._request_keys_by_id: dict[int, str] = {}
        self._external_references: dict[int, str] = {}
        self._next_id = 1

    def _in_scope(
        self,
        claim_id: int,
        principal: AuthenticatedPrincipal,
    ) -> bool:
        return (
            principal.role is PrincipalRole.SUPERVISOR
            or claim_id in self._visible
        )

    def find_request(
        self,
        idempotency_key: str,
        principal: AuthenticatedPrincipal,
    ) -> StoredAssistanceRequest | None:
        stored = self._requests.get(idempotency_key)
        if stored is None or not self._in_scope(
            stored.result.claim_id,
            principal,
        ):
            return None
        return stored

    def create(
        self,
        command: RequestAssistanceCommand,
        principal: AuthenticatedPrincipal,
        *,
        idempotency_key: str,
        fingerprint: str,
    ) -> AssistanceRecord:
        if not self._in_scope(command.claim_id, principal):
            raise AssistanceRequestError(
                "CLAIM-NOT-FOUND",
                "Siniestro no encontrado",
                404,
            )
        now = datetime.now(timezone.utc)
        result = AssistanceRecord(
            id=self._next_id,
            claim_id=command.claim_id,
            provider_id=command.provider_id,
            assistance_type=command.assistance_type,
            status=AssistanceStatus.PENDING,
            attempt=1,
            created_at=now,
            updated_at=now,
        )
        self._next_id += 1
        self._records[result.id] = result
        self._requests[idempotency_key] = StoredAssistanceRequest(
            fingerprint,
            result,
        )
        self._request_keys_by_id[result.id] = idempotency_key
        return result

    def mark_sent(
        self,
        assistance_id: int,
        external_reference: str,
        principal: AuthenticatedPrincipal,
    ) -> AssistanceRecord:
        current = self._records[assistance_id]
        if not self._in_scope(current.claim_id, principal):
            raise AssistanceRequestError(
                "CLAIM-NOT-FOUND",
                "Siniestro no encontrado",
                404,
            )
        sent = AssistanceRecord(
            id=current.id,
            claim_id=current.claim_id,
            provider_id=current.provider_id,
            assistance_type=current.assistance_type,
            status=AssistanceStatus.SENT,
            attempt=current.attempt,
            created_at=current.created_at,
            updated_at=datetime.now(timezone.utc),
        )
        self._records[assistance_id] = sent
        self._external_references[assistance_id] = external_reference
        key = self._request_keys_by_id[assistance_id]
        stored = self._requests[key]
        self._requests[key] = StoredAssistanceRequest(
            stored.fingerprint,
            sent,
        )
        return sent

    def get(
        self,
        claim_id: int,
        assistance_id: int,
        principal: AuthenticatedPrincipal,
    ) -> AssistanceRecord | None:
        result = self._records.get(assistance_id)
        if (
            result is None
            or result.claim_id != claim_id
            or not self._in_scope(claim_id, principal)
        ):
            return None
        return result


class RequestAssistanceService:
    def __init__(
        self,
        repository: RequestAssistanceRepository,
        provider: ProviderAdapter,
    ) -> None:
        self._repository = repository
        self._provider = provider

    def execute(
        self,
        command: RequestAssistanceCommand,
        principal: AuthenticatedPrincipal,
        *,
        idempotency_key: str,
        request_payload: object,
    ) -> AssistanceRecord:
        try:
            authorize(
                principal.role,
                Action.SOLICITAR_ASISTENCIA,
                resource_in_scope=True,
            )
        except AuthorizationDenied as exc:
            raise AssistanceRequestError(
                "ACTION-NOT-ALLOWED",
                "Acción no permitida para el rol",
                403,
            ) from exc

        try:
            key = validate_idempotency_key(idempotency_key)
        except ValueError as exc:
            raise AssistanceRequestError(
                "IDEMPOTENCY-INVALID",
                str(exc),
                422,
            ) from exc

        assistance_type = command.assistance_type.strip().lower()
        reason = command.reason.strip()
        if command.provider_id <= 0:
            raise AssistanceRequestError(
                "PROVIDER-INVALID",
                "El proveedor debe ser válido",
                422,
            )
        if not assistance_type or not reason:
            raise AssistanceRequestError(
                "ASSISTANCE-DATA-INVALID",
                "Tipo de asistencia y motivo son obligatorios",
                422,
            )

        fingerprint = fingerprint_request(request_payload)
        stored = self._repository.find_request(key, principal)
        if stored is not None:
            if stored.fingerprint != fingerprint:
                raise AssistanceRequestError(
                    "IDEMPOTENCY-CONFLICT",
                    "Idempotency-Key ya fue utilizada con otro contenido",
                    409,
                )
            return stored.result

        normalized = RequestAssistanceCommand(
            claim_id=command.claim_id,
            provider_id=command.provider_id,
            assistance_type=assistance_type,
            reason=reason,
        )
        created = self._repository.create(
            normalized,
            principal,
            idempotency_key=key,
            fingerprint=fingerprint,
        )
        external_reference = dispatch_assistance(
            self._provider,
            created,
            idempotency_key=key,
        )
        return self._repository.mark_sent(
            created.id,
            external_reference,
            principal,
        )


class GetAssistanceService:
    def __init__(self, repository: RequestAssistanceRepository) -> None:
        self._repository = repository

    def execute(
        self,
        claim_id: int,
        assistance_id: int,
        principal: AuthenticatedPrincipal,
    ) -> AssistanceRecord:
        try:
            authorize(
                principal.role,
                Action.CONSULTAR_SINIESTRO,
                resource_in_scope=True,
            )
        except AuthorizationDenied as exc:
            raise AssistanceRequestError(
                "ACTION-NOT-ALLOWED",
                "Acción no permitida para el rol",
                403,
            ) from exc
        result = self._repository.get(
            claim_id,
            assistance_id,
            principal,
        )
        if result is None:
            raise AssistanceRequestError(
                "ASSISTANCE-NOT-FOUND",
                "Asistencia no encontrada",
                404,
            )
        return result
