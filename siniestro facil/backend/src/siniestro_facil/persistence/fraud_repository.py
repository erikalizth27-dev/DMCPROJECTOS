from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from siniestro_facil.application.evaluate_fraud import (
    FraudEvaluationError,
    FraudEvaluationResult,
    GeneratedAlert,
    ReviewAlertCommand,
    ReviewedAlert,
    StoredFraudRequest,
    StoredReviewRequest,
)
from siniestro_facil.domain.fraud import (
    AlertReviewStatus,
    AlertSeverity,
    effect_for_severity,
)
from siniestro_facil.domain.identity import AuthenticatedPrincipal
from siniestro_facil.infrastructure.fraud_adapter import FraudEvaluation
from siniestro_facil.persistence.models import (
    Alerta,
    EventoLineaTiempo,
    IdentidadActor,
    PoliticaAlerta,
    SenalRiesgo,
    Siniestro,
    SolicitudEvaluacionFraudeIdempotente,
    SolicitudRevisionAlertaIdempotente,
)


class PostgreSQLFraudAlertRepository:
    def __init__(self, factory: sessionmaker[Session]) -> None:
        self._factory = factory

    @staticmethod
    def _serialize(result: FraudEvaluationResult) -> dict[str, object]:
        return {
            "claim_id": result.claim_id,
            "alerts": [
                {
                    "id": alert.id,
                    "claim_id": alert.claim_id,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity.value,
                    "explanation": alert.explanation,
                    "source_data": alert.source_data,
                    "rule_or_model": alert.rule_or_model,
                    "policy_version": alert.policy_version,
                    "effect": alert.effect.value,
                    "review_status": alert.review_status.value,
                    "version": alert.version,
                }
                for alert in result.alerts
            ],
        }

    @staticmethod
    def _deserialize(payload: dict[str, object]) -> FraudEvaluationResult:
        rows = payload.get("alerts", [])
        alerts = tuple(
            GeneratedAlert(
                id=int(row["id"]),
                claim_id=int(row["claim_id"]),
                alert_type=str(row["alert_type"]),
                severity=AlertSeverity(str(row["severity"])),
                explanation=str(row["explanation"]),
                source_data=dict(row["source_data"]),
                rule_or_model=str(row["rule_or_model"]),
                policy_version=str(row["policy_version"]),
                effect=effect_for_severity(AlertSeverity(str(row["severity"]))),
                review_status=AlertReviewStatus(str(row["review_status"])),
                version=int(row.get("version", 0)),
            )
            for row in rows
            if isinstance(row, dict)
        )
        return FraudEvaluationResult(int(payload["claim_id"]), alerts)

    def find_request(self, idempotency_key: str) -> StoredFraudRequest | None:
        with self._factory() as session:
            row = session.get(
                SolicitudEvaluacionFraudeIdempotente,
                idempotency_key,
            )
            if row is None:
                return None
            return StoredFraudRequest(
                row.huella,
                self._deserialize(row.respuesta),
            )

    def create(
        self,
        claim_id: int,
        evaluation: FraudEvaluation,
        principal: AuthenticatedPrincipal,
        *,
        idempotency_key: str,
        fingerprint: str,
    ) -> FraudEvaluationResult:
        try:
            with self._factory() as session, session.begin():
                existing = session.get(
                    SolicitudEvaluacionFraudeIdempotente,
                    idempotency_key,
                    with_for_update=True,
                )
                if existing is not None:
                    if existing.huella == fingerprint:
                        return self._deserialize(existing.respuesta)
                    raise FraudEvaluationError(
                        "IDEMPOTENCY-CONFLICT",
                        "Idempotency-Key ya fue utilizada con otro contenido",
                        409,
                    )

                claim = session.get(Siniestro, claim_id, with_for_update=True)
                if claim is None:
                    raise FraudEvaluationError(
                        "CLAIM-NOT-FOUND",
                        "Siniestro no encontrado",
                        404,
                    )
                identity = session.get(
                    IdentidadActor,
                    (principal.subject, principal.tenant_id),
                )
                if identity is None or identity.id_usuario is None:
                    raise FraudEvaluationError(
                        "FRAUD-EVALUATION-FORBIDDEN",
                        "Identidad interna no vinculada",
                        403,
                    )

                policy_versions = {
                    recommendation.policy_version
                    for recommendation in evaluation.alerts
                }
                policies = {
                    row.version: row
                    for row in session.execute(
                        select(PoliticaAlerta).where(
                            PoliticaAlerta.version.in_(policy_versions)
                        )
                    ).scalars()
                } if policy_versions else {}
                if policy_versions != set(policies):
                    raise FraudEvaluationError(
                        "FRAUD-POLICY-NOT-FOUND",
                        "Política antifraude versionada no encontrada",
                        409,
                    )

                now = datetime.now(timezone.utc)
                generated: list[GeneratedAlert] = []
                for signal in evaluation.signals:
                    session.add(
                        SenalRiesgo(
                            id_siniestro=claim_id,
                            tipo_senal=signal.signal_type.value,
                            origen=signal.origin.value,
                        )
                    )
                for recommendation in evaluation.alerts:
                    row = Alerta(
                        id_siniestro=claim_id,
                        tipo=recommendation.alert_type,
                        severidad=recommendation.severity.value,
                        explicacion=recommendation.explanation,
                        datos_origen=recommendation.source_data,
                        fecha=now,
                        modelo_o_regla=recommendation.rule_or_model,
                        id_politica_alerta=policies[
                            recommendation.policy_version
                        ].id_politica_alerta,
                        estado_revision=AlertReviewStatus.PENDIENTE.value,
                        justificacion_revision=None,
                        version=0,
                    )
                    session.add(row)
                    session.flush()
                    generated.append(
                        GeneratedAlert(
                            id=row.id_alerta,
                            claim_id=claim_id,
                            alert_type=recommendation.alert_type,
                            severity=recommendation.severity,
                            explanation=recommendation.explanation,
                            source_data=recommendation.source_data,
                            rule_or_model=recommendation.rule_or_model,
                            policy_version=recommendation.policy_version,
                            effect=recommendation.effect,
                        )
                    )
                result = FraudEvaluationResult(claim_id, tuple(generated))
                session.add(
                    EventoLineaTiempo(
                        id_siniestro=claim_id,
                        id_usuario=identity.id_usuario,
                        tipo_evento="evaluacion_fraude_ejecutada",
                        fecha=now,
                        detalle={
                            "alertas_generadas": len(generated),
                            "politicas": sorted(policy_versions),
                        },
                    )
                )
                session.add(
                    SolicitudEvaluacionFraudeIdempotente(
                        clave=idempotency_key,
                        huella=fingerprint,
                        id_siniestro=claim_id,
                        respuesta=self._serialize(result),
                        creado_en=now,
                    )
                )
            return result
        except IntegrityError as exc:
            stored = self.find_request(idempotency_key)
            if stored is not None and stored.fingerprint == fingerprint:
                return stored.result
            if stored is not None:
                raise FraudEvaluationError(
                    "IDEMPOTENCY-CONFLICT",
                    "Idempotency-Key ya fue utilizada con otro contenido",
                    409,
                ) from exc
            raise

    def get_alert(self, claim_id: int, alert_id: int) -> GeneratedAlert | None:
        with self._factory() as session:
            row = session.execute(
                select(Alerta, PoliticaAlerta.version)
                .join(
                    PoliticaAlerta,
                    PoliticaAlerta.id_politica_alerta
                    == Alerta.id_politica_alerta,
                )
                .where(
                    Alerta.id_siniestro == claim_id,
                    Alerta.id_alerta == alert_id,
                )
            ).one_or_none()
            if row is None:
                return None
            alert, policy_version = row
            severity = AlertSeverity(alert.severidad)
            return GeneratedAlert(
                id=alert.id_alerta,
                claim_id=alert.id_siniestro,
                alert_type=alert.tipo,
                severity=severity,
                explanation=alert.explicacion,
                source_data=dict(alert.datos_origen),
                rule_or_model=alert.modelo_o_regla,
                policy_version=policy_version,
                effect=effect_for_severity(severity),
                review_status=AlertReviewStatus(alert.estado_revision),
                version=alert.version,
            )


    @staticmethod
    def _serialize_review(result: ReviewedAlert) -> dict[str, object]:
        return {
            "alert_id": result.alert_id,
            "claim_id": result.claim_id,
            "review_status": result.review_status.value,
            "justification": result.justification,
            "version": result.version,
            "reviewer_subject": result.reviewer_subject,
        }

    @staticmethod
    def _deserialize_review(payload: dict[str, object]) -> ReviewedAlert:
        return ReviewedAlert(
            alert_id=int(payload["alert_id"]),
            claim_id=int(payload["claim_id"]),
            review_status=AlertReviewStatus(str(payload["review_status"])),
            justification=str(payload["justification"]),
            version=int(payload["version"]),
            reviewer_subject=str(payload["reviewer_subject"]),
        )

    def find_review_request(
        self, idempotency_key: str
    ) -> StoredReviewRequest | None:
        with self._factory() as session:
            row = session.get(
                SolicitudRevisionAlertaIdempotente,
                idempotency_key,
            )
            if row is None:
                return None
            return StoredReviewRequest(
                row.huella,
                self._deserialize_review(row.respuesta),
            )

    def review(
        self,
        command: ReviewAlertCommand,
        principal: AuthenticatedPrincipal,
        *,
        idempotency_key: str,
        fingerprint: str,
    ) -> ReviewedAlert:
        try:
            with self._factory() as session, session.begin():
                existing = session.get(
                    SolicitudRevisionAlertaIdempotente,
                    idempotency_key,
                    with_for_update=True,
                )
                if existing is not None:
                    if existing.huella == fingerprint:
                        return self._deserialize_review(existing.respuesta)
                    raise FraudEvaluationError(
                        "IDEMPOTENCY-CONFLICT",
                        "Idempotency-Key ya fue utilizada con otro contenido",
                        409,
                    )
                alert = session.execute(
                    select(Alerta)
                    .where(
                        Alerta.id_alerta == command.alert_id,
                        Alerta.id_siniestro == command.claim_id,
                    )
                    .with_for_update()
                ).scalar_one_or_none()
                if alert is None:
                    raise FraudEvaluationError(
                        "ALERT-NOT-FOUND", "Alerta no encontrada", 404
                    )
                identity = session.get(
                    IdentidadActor,
                    (principal.subject, principal.tenant_id),
                )
                if identity is None or identity.id_usuario is None:
                    raise FraudEvaluationError(
                        "ALERT-REVIEW-FORBIDDEN",
                        "Identidad interna no vinculada",
                        403,
                    )
                if alert.version != command.expected_version:
                    raise FraudEvaluationError(
                        "ALERT-VERSION-CONFLICT",
                        "La alerta fue modificada por otra revisión",
                        409,
                    )
                if alert.estado_revision != AlertReviewStatus.PENDIENTE.value:
                    raise FraudEvaluationError(
                        "ALERT-ALREADY-REVIEWED",
                        "La alerta ya tiene una decisión humana",
                        409,
                    )
                now = datetime.now(timezone.utc)
                alert.estado_revision = command.target.value
                alert.justificacion_revision = command.justification.strip()
                alert.version += 1
                result = ReviewedAlert(
                    alert_id=alert.id_alerta,
                    claim_id=alert.id_siniestro,
                    review_status=command.target,
                    justification=alert.justificacion_revision,
                    version=alert.version,
                    reviewer_subject=principal.subject,
                )
                session.add(
                    EventoLineaTiempo(
                        id_siniestro=alert.id_siniestro,
                        id_usuario=identity.id_usuario,
                        tipo_evento="alerta_fraude_revisada",
                        fecha=now,
                        detalle={
                            "id_alerta": alert.id_alerta,
                            "estado_revision": command.target.value,
                            "justificacion": alert.justificacion_revision,
                            "version": alert.version,
                        },
                    )
                )
                session.add(
                    SolicitudRevisionAlertaIdempotente(
                        clave=idempotency_key,
                        huella=fingerprint,
                        id_alerta=alert.id_alerta,
                        respuesta=self._serialize_review(result),
                        creado_en=now,
                    )
                )
            return result
        except IntegrityError as exc:
            stored = self.find_review_request(idempotency_key)
            if stored is not None and stored.fingerprint == fingerprint:
                return stored.result
            if stored is not None:
                raise FraudEvaluationError(
                    "IDEMPOTENCY-CONFLICT",
                    "Idempotency-Key ya fue utilizada con otro contenido",
                    409,
                ) from exc
            raise

    def audit_alert_access(
        self,
        claim_id: int,
        alert_id: int,
        principal: AuthenticatedPrincipal,
    ) -> None:
        with self._factory() as session, session.begin():
            identity = session.get(
                IdentidadActor,
                (principal.subject, principal.tenant_id),
            )
            if identity is None or identity.id_usuario is None:
                raise FraudEvaluationError(
                    "ALERT-NOT-FOUND", "Alerta no encontrada", 404
                )
            session.add(
                EventoLineaTiempo(
                    id_siniestro=claim_id,
                    id_usuario=identity.id_usuario,
                    tipo_evento="acceso_alerta_fraude_sensible",
                    fecha=datetime.now(timezone.utc),
                    detalle={"id_alerta": alert_id},
                )
            )
