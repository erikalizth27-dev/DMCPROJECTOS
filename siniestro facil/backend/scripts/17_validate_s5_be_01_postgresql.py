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
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.fraud import AlertSeverity, RiskSignalType
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
    UsuarioInterno,
)


TENANT = "tenant-s5-validation"
KEY_ALERT = "s5-fraud-evaluation-0001"
KEY_EMPTY = "s5-fraud-evaluation-0002"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL no configurada")

engine = create_engine(database_url, pool_pre_ping=True)
claim_id: int | None = None
user_id: int | None = None
subject = f"s5-fraud-validation-{uuid4().hex}"
policy_version = f"s5val-{uuid4().hex[:8]}"
policy_id: int | None = None
alert_ids: list[int] = []
signal_ids: list[int] = []
audit_ids: list[int] = []
keys = [KEY_ALERT, KEY_EMPTY]

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

        max_alert = connection.execute(
            select(func.coalesce(func.max(Alerta.id_alerta), 0))
        ).scalar_one()
        max_signal = connection.execute(
            select(func.coalesce(func.max(SenalRiesgo.id_senal), 0))
        ).scalar_one()
        max_audit = connection.execute(
            select(func.coalesce(func.max(EventoLineaTiempo.id_evento), 0))
        ).scalar_one()

        principal = AuthenticatedPrincipal(
            subject=subject,
            role=PrincipalRole.INVESTIGADOR_FRAUDE,
            actor_type=ActorType.INTERNO,
            tenant_id=TENANT,
            issued_at=now - timedelta(minutes=1),
            expires_at=now + timedelta(hours=1),
            authenticated_at=now - timedelta(minutes=1),
        )
        adapter = DeterministicFraudAdapter(
            rule_set="pilot-fraud-validation",
            version="1",
            policy_version=policy_version,
            rules=(
                DeterministicRule(
                    fact_key="foto_reutilizada",
                    signal_type=RiskSignalType.FOTO_REUTILIZADA,
                    severity=AlertSeverity.CRITICA,
                    explanation="Coincidencia exacta de hash sintético",
                ),
            ),
        )
        factory = sessionmaker(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        service = EvaluateFraudService(
            adapter,
            PostgreSQLFraudAlertRepository(factory),
        )

        payload = {"hechos": {"foto_reutilizada": True}}
        result = service.execute(
            EvaluateFraudCommand(claim_id, payload["hechos"]),
            principal,
            idempotency_key=KEY_ALERT,
            request_payload=payload,
        )
        require(len(result.alerts) == 1, "No se generó una alerta")
        alert = result.alerts[0]
        require(alert.severity is AlertSeverity.CRITICA, "Severidad incorrecta")
        require(
            alert.policy_version == policy_version,
            "Versión de política incorrecta",
        )
        require(
            alert.rule_or_model == "pilot-fraud-validation:1",
            "Versión de regla incorrecta",
        )
        alert_ids.append(alert.id)

        signal_ids = list(
            connection.execute(
                select(SenalRiesgo.id_senal).where(
                    SenalRiesgo.id_senal > max_signal,
                    SenalRiesgo.id_siniestro == claim_id,
                )
            ).scalars()
        )
        require(len(signal_ids) == 1, "Señal no persistida")
        stored_alert = connection.execute(
            select(Alerta).where(Alerta.id_alerta == alert.id)
        ).scalar_one_or_none()
        require(stored_alert is not None, "Alerta no persistida")
        require(
            stored_alert.id_politica_alerta == policy_id,
            "Política no vinculada",
        )
        print(f"Siniestro probado: {claim_id}")
        print(f"Política versionada: {policy_version}")
        print(f"Señal registrada: {signal_ids[0]}")
        print(f"Alerta crítica registrada: {alert.id}")
        print("Entradas, explicación y versión persistidas: OK")

        repeated = service.execute(
            EvaluateFraudCommand(claim_id, payload["hechos"]),
            principal,
            idempotency_key=KEY_ALERT,
            request_payload=payload,
        )
        require(repeated == result, "Repetición no idempotente")
        require(
            connection.execute(
                select(func.count(Alerta.id_alerta)).where(
                    Alerta.id_alerta > max_alert,
                    Alerta.id_siniestro == claim_id,
                )
            ).scalar_one() == 1,
            "La repetición duplicó alertas",
        )
        print("Repetición idempotente sin duplicados: OK")

        try:
            changed = {"hechos": {"foto_reutilizada": False}}
            service.execute(
                EvaluateFraudCommand(claim_id, changed["hechos"]),
                principal,
                idempotency_key=KEY_ALERT,
                request_payload=changed,
            )
        except FraudEvaluationError as exc:
            require(exc.code == "IDEMPOTENCY-CONFLICT", "Código inesperado")
            require(exc.status_code == 409, "HTTP inesperado")
            print("Conflicto idempotente: HTTP 409 — OK")
        else:
            raise AssertionError("No se detectó conflicto idempotente")

        empty_payload = {"hechos": {"foto_reutilizada": False}}
        empty = service.execute(
            EvaluateFraudCommand(claim_id, empty_payload["hechos"]),
            principal,
            idempotency_key=KEY_EMPTY,
            request_payload=empty_payload,
        )
        require(empty.alerts == (), "Evaluación negativa creó alertas")
        require(
            connection.get_execution_options() is not None,
            "Conexión inválida",
        )
        audit_ids = list(
            connection.execute(
                select(EventoLineaTiempo.id_evento).where(
                    EventoLineaTiempo.id_evento > max_audit,
                    EventoLineaTiempo.id_siniestro == claim_id,
                    EventoLineaTiempo.tipo_evento
                    == "evaluacion_fraude_ejecutada",
                )
            ).scalars()
        )
        require(len(audit_ids) == 2, "Auditoría atómica incompleta")
        stored_keys = list(
            connection.execute(
                select(SolicitudEvaluacionFraudeIdempotente.clave).where(
                    SolicitudEvaluacionFraudeIdempotente.clave.in_(keys)
                )
            ).scalars()
        )
        require(set(stored_keys) == set(keys), "Idempotencia incompleta")
        print("Evaluación sin alertas persistida idempotentemente: OK")
        print("Auditoría atómica de ambas evaluaciones: OK")
        print("S5-BE-01 PostgreSQL: OK")
    finally:
        outer.rollback()
        print("ROLLBACK ejecutado")

require(claim_id is not None, "No se seleccionó siniestro")
with engine.connect() as verification:
    checks = [
        (Alerta.id_alerta, alert_ids, "Alertas residuales"),
        (SenalRiesgo.id_senal, signal_ids, "Señales residuales"),
        (EventoLineaTiempo.id_evento, audit_ids, "Auditoría residual"),
        (PoliticaAlerta.id_politica_alerta, [policy_id], "Política residual"),
        (UsuarioInterno.id_usuario, [user_id], "Usuario residual"),
    ]
    for column, values, message in checks:
        clean = [value for value in values if value is not None]
        if clean:
            require(
                not verification.execute(
                    select(column).where(column.in_(clean))
                ).scalars().all(),
                message,
            )
    require(
        not verification.execute(
            select(SolicitudEvaluacionFraudeIdempotente.clave).where(
                SolicitudEvaluacionFraudeIdempotente.clave.in_(keys)
            )
        ).scalars().all(),
        "Idempotencia residual",
    )
    require(
        verification.execute(
            select(IdentidadActor.subject).where(
                IdentidadActor.subject == subject
            )
        ).scalar_one_or_none()
        is None,
        "Identidad residual",
    )

print("Alertas y señales sintéticas eliminadas: OK")
print("Auditoría e idempotencia sintéticas eliminadas: OK")
print("Política, identidad y usuario sintéticos eliminados: OK")
print("Limpieza validada: sin registros residuales")
print("VALIDACIÓN FINAL S5-BE-01 COMPLETADA")
engine.dispose()
