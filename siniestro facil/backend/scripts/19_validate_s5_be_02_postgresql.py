from __future__ import annotations

import os
from datetime import date, datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import create_engine, func, insert, select
from sqlalchemy.orm import sessionmaker

from siniestro_facil.application.evaluate_fraud import (
    EvaluateFraudCommand,
    EvaluateFraudService,
    FraudEvaluationError,
    GetFraudAlertService,
    ReviewAlertCommand,
    ReviewFraudAlertService,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.fraud import (
    AlertReviewStatus,
    AlertSeverity,
    RiskSignalType,
)
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal
from siniestro_facil.infrastructure.fraud_adapter import (
    DeterministicFraudAdapter,
    DeterministicRule,
)
from siniestro_facil.persistence.fraud_repository import (
    PostgreSQLFraudAlertRepository,
)
from siniestro_facil.persistence.models import (
    Alerta,
    EventoLineaTiempo,
    IdentidadActor,
    PoliticaAlerta,
    SenalRiesgo,
    Siniestro,
    SolicitudEvaluacionFraudeIdempotente,
    SolicitudRevisionAlertaIdempotente,
    UsuarioInterno,
)


TENANT = "tenant-s5-review-validation"
EVALUATION_KEY = "s5-review-evaluation-0001"
REVIEW_KEY = "s5-alert-review-validation-0001"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def principal(subject: str, role: PrincipalRole, now: datetime):
    return AuthenticatedPrincipal(
        subject=subject,
        role=role,
        actor_type=ActorType.INTERNO,
        tenant_id=TENANT,
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL no configurada")

engine = create_engine(database_url, pool_pre_ping=True)
claim_id: int | None = None
user_id: int | None = None
policy_id: int | None = None
alert_id: int | None = None
signal_ids: list[int] = []
audit_ids: list[int] = []
subject = f"s5-review-validation-{uuid4().hex}"
policy_version = f"s5rev-{uuid4().hex[:8]}"

with engine.connect() as connection:
    outer = connection.begin()
    try:
        claim_id = connection.execute(
            select(Siniestro.id_siniestro)
            .order_by(Siniestro.id_siniestro)
            .limit(1)
        ).scalar_one_or_none()
        require(claim_id is not None, "No existe siniestro para validar")
        now = datetime.now(timezone.utc)

        user_id = connection.execute(
            insert(UsuarioInterno)
            .values(rol=PrincipalRole.INVESTIGADOR_FRAUDE.value)
            .returning(UsuarioInterno.id_usuario)
        ).scalar_one()
        connection.execute(
            insert(IdentidadActor).values(
                subject=subject,
                tenant_id=TENANT,
                actor_type=ActorType.INTERNO.value,
                id_usuario=user_id,
            )
        )
        policy_id = connection.execute(
            insert(PoliticaAlerta)
            .values(
                version=policy_version,
                regla_bloqueo={
                    "critica": "bloquear_pago_hasta_revision",
                    "declaracion_automatica_fraude": False,
                },
                vigente_desde=date.today(),
            )
            .returning(PoliticaAlerta.id_politica_alerta)
        ).scalar_one()

        max_signal = connection.execute(
            select(func.coalesce(func.max(SenalRiesgo.id_senal), 0))
        ).scalar_one()
        max_audit = connection.execute(
            select(func.coalesce(func.max(EventoLineaTiempo.id_evento), 0))
        ).scalar_one()

        investigator = principal(
            subject, PrincipalRole.INVESTIGADOR_FRAUDE, now
        )
        operator = principal(
            f"operator-summary-{uuid4().hex}",
            PrincipalRole.OPERADOR,
            now,
        )
        factory = sessionmaker(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        repository = PostgreSQLFraudAlertRepository(factory)
        adapter = DeterministicFraudAdapter(
            rule_set="pilot-review-validation",
            version="1",
            policy_version=policy_version,
            rules=(
                DeterministicRule(
                    fact_key="foto_reutilizada",
                    signal_type=RiskSignalType.FOTO_REUTILIZADA,
                    severity=AlertSeverity.CRITICA,
                    explanation="Hash sintético para revisión humana",
                ),
            ),
        )
        payload = {"hechos": {"foto_reutilizada": True}}
        generated = EvaluateFraudService(adapter, repository).execute(
            EvaluateFraudCommand(claim_id, payload["hechos"]),
            investigator,
            idempotency_key=EVALUATION_KEY,
            request_payload=payload,
        )
        require(len(generated.alerts) == 1, "No se generó alerta")
        alert_id = generated.alerts[0].id
        signal_ids = list(
            connection.execute(
                select(SenalRiesgo.id_senal).where(
                    SenalRiesgo.id_senal > max_signal,
                    SenalRiesgo.id_siniestro == claim_id,
                )
            ).scalars()
        )

        review_payload = {
            "estado": AlertReviewStatus.CONFIRMADA.value,
            "justificacion": "Confirmación humana sintética documentada",
            "version": 0,
        }
        command = ReviewAlertCommand(
            claim_id=claim_id,
            alert_id=alert_id,
            target=AlertReviewStatus.CONFIRMADA,
            justification=review_payload["justificacion"],
            expected_version=0,
        )
        review_service = ReviewFraudAlertService(repository)
        reviewed = review_service.execute(
            command,
            investigator,
            idempotency_key=REVIEW_KEY,
            request_payload=review_payload,
        )
        require(reviewed.version == 1, "Versión no incrementada")
        require(
            reviewed.review_status is AlertReviewStatus.CONFIRMADA,
            "Estado de revisión incorrecto",
        )
        state, justification, version = connection.execute(
            select(
                Alerta.estado_revision,
                Alerta.justificacion_revision,
                Alerta.version,
            ).where(Alerta.id_alerta == alert_id)
        ).one()
        require(state == "confirmada", "Decisión no persistida")
        require(
            justification == review_payload["justificacion"],
            "Justificación no persistida",
        )
        require(version == 1, "Versión física incorrecta")
        print(f"Siniestro probado: {claim_id}")
        print(f"Alerta revisada: {alert_id}")
        print("Decisión, justificación y versión persistidas: OK")

        repeated = review_service.execute(
            command,
            investigator,
            idempotency_key=REVIEW_KEY,
            request_payload=review_payload,
        )
        require(repeated == reviewed, "Repetición no idempotente")
        print("Repetición idempotente: OK")

        try:
            changed = {
                **review_payload,
                "estado": AlertReviewStatus.DESCARTADA.value,
            }
            review_service.execute(
                ReviewAlertCommand(
                    claim_id,
                    alert_id,
                    AlertReviewStatus.DESCARTADA,
                    review_payload["justificacion"],
                    0,
                ),
                investigator,
                idempotency_key=REVIEW_KEY,
                request_payload=changed,
            )
        except FraudEvaluationError as exc:
            require(exc.code == "IDEMPOTENCY-CONFLICT", "Código inesperado")
            require(exc.status_code == 409, "HTTP inesperado")
            print("Conflicto idempotente: HTTP 409 — OK")
        else:
            raise AssertionError("No se detectó conflicto idempotente")

        getter = GetFraudAlertService(repository)
        before_sensitive = connection.execute(
            select(func.count(EventoLineaTiempo.id_evento)).where(
                EventoLineaTiempo.id_siniestro == claim_id,
                EventoLineaTiempo.tipo_evento
                == "acceso_alerta_fraude_sensible",
            )
        ).scalar_one()
        summary = getter.execute(claim_id, alert_id, operator)
        require(summary.explanation is None, "Resumen expuso detalle")
        after_summary = connection.execute(
            select(func.count(EventoLineaTiempo.id_evento)).where(
                EventoLineaTiempo.id_siniestro == claim_id,
                EventoLineaTiempo.tipo_evento
                == "acceso_alerta_fraude_sensible",
            )
        ).scalar_one()
        require(
            after_summary == before_sensitive,
            "Consulta de resumen se auditó como sensible",
        )
        detail = getter.execute(claim_id, alert_id, investigator)
        require(
            detail.explanation == "Hash sintético para revisión humana",
            "Detalle autorizado incompleto",
        )
        after_detail = connection.execute(
            select(func.count(EventoLineaTiempo.id_evento)).where(
                EventoLineaTiempo.id_siniestro == claim_id,
                EventoLineaTiempo.tipo_evento
                == "acceso_alerta_fraude_sensible",
            )
        ).scalar_one()
        require(
            after_detail == before_sensitive + 1,
            "Acceso sensible no auditado",
        )
        print("Resumen operativo sin detalle sensible: OK")
        print("Acceso detallado auditado con identidad: OK")

        audit_ids = list(
            connection.execute(
                select(EventoLineaTiempo.id_evento).where(
                    EventoLineaTiempo.id_evento > max_audit,
                    EventoLineaTiempo.id_siniestro == claim_id,
                )
            ).scalars()
        )
        types = set(
            connection.execute(
                select(EventoLineaTiempo.tipo_evento).where(
                    EventoLineaTiempo.id_evento.in_(audit_ids)
                )
            ).scalars()
        )
        require("alerta_fraude_revisada" in types, "Falta auditoría de revisión")
        require(
            "acceso_alerta_fraude_sensible" in types,
            "Falta auditoría sensible",
        )
        require(
            connection.execute(
                select(SolicitudRevisionAlertaIdempotente.clave).where(
                    SolicitudRevisionAlertaIdempotente.clave == REVIEW_KEY
                )
            ).scalar_one_or_none() == REVIEW_KEY,
            "Idempotencia de revisión no persistida",
        )
        print("Auditoría atómica de revisión: OK")
        print("S5-BE-02 PostgreSQL: OK")
    finally:
        outer.rollback()
        print("ROLLBACK ejecutado")

require(claim_id is not None, "No se seleccionó siniestro")
with engine.connect() as verification:
    checks = [
        (Alerta.id_alerta, alert_id, "Alerta residual"),
        (PoliticaAlerta.id_politica_alerta, policy_id, "Política residual"),
        (UsuarioInterno.id_usuario, user_id, "Usuario residual"),
    ]
    for column, value, message in checks:
        if value is not None:
            require(
                verification.execute(
                    select(column).where(column == value)
                ).scalar_one_or_none() is None,
                message,
            )
    if signal_ids:
        require(
            not verification.execute(
                select(SenalRiesgo.id_senal).where(
                    SenalRiesgo.id_senal.in_(signal_ids)
                )
            ).scalars().all(),
            "Señales residuales",
        )
    if audit_ids:
        require(
            not verification.execute(
                select(EventoLineaTiempo.id_evento).where(
                    EventoLineaTiempo.id_evento.in_(audit_ids)
                )
            ).scalars().all(),
            "Auditoría residual",
        )
    require(
        verification.execute(
            select(SolicitudEvaluacionFraudeIdempotente.clave).where(
                SolicitudEvaluacionFraudeIdempotente.clave == EVALUATION_KEY
            )
        ).scalar_one_or_none() is None,
        "Idempotencia de evaluación residual",
    )
    require(
        verification.execute(
            select(SolicitudRevisionAlertaIdempotente.clave).where(
                SolicitudRevisionAlertaIdempotente.clave == REVIEW_KEY
            )
        ).scalar_one_or_none() is None,
        "Idempotencia de revisión residual",
    )
    require(
        verification.execute(
            select(IdentidadActor.subject).where(
                IdentidadActor.subject == subject
            )
        ).scalar_one_or_none() is None,
        "Identidad residual",
    )

print("Alerta, señal y política sintéticas eliminadas: OK")
print("Revisión, auditoría e idempotencia eliminadas: OK")
print("Identidad y usuario sintéticos eliminados: OK")
print("Limpieza validada: sin registros residuales")
print("VALIDACIÓN FINAL S5-BE-02 COMPLETADA")
engine.dispose()
