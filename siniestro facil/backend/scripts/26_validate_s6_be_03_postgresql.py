from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import create_engine, insert, select
from sqlalchemy.orm import sessionmaker

from siniestro_facil.application.get_operational_metrics import (
    GetOperationalMetricsService,
    OperationalMetricsError,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal
from siniestro_facil.domain.operational_metrics import (
    IndicatorAvailability,
    IndicatorName,
)
from siniestro_facil.persistence.models import (
    Asistencia,
    EventoLineaTiempo,
    IdentidadActor,
    Proveedor,
    Siniestro,
    UsuarioInterno,
)
from siniestro_facil.persistence.operational_metrics_repository import (
    PostgreSQLOperationalMetricsRepository,
)


TENANT = "tenant-s6-metrics-validation"
MARKER = "Validación sintética S6-BE-03"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def make_principal(
    *,
    subject: str,
    role: PrincipalRole,
    now: datetime,
) -> AuthenticatedPrincipal:
    return AuthenticatedPrincipal(
        subject=subject,
        tenant_id=TENANT,
        actor_type=ActorType.INTERNO,
        role=role,
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL no configurada")

engine = create_engine(database_url, pool_pre_ping=True)
token = uuid4().hex
subject = f"s6-metrics-supervisor-{token}"
claim_id: int | None = None
provider_id: int | None = None
assistance_id: int | None = None
decision_event_id: int | None = None
user_id: int | None = None

with engine.connect() as connection:
    outer = connection.begin()
    try:
        source = connection.execute(
            select(
                Siniestro.id_poliza,
                Siniestro.id_vehiculo,
                Siniestro.id_reportante,
                Siniestro.tipo_evento,
            )
            .order_by(Siniestro.id_siniestro)
            .limit(1)
        ).one_or_none()
        require(source is not None, "No existe siniestro base para validar")

        now = datetime.now(timezone.utc)
        claim_created_at = now + timedelta(days=30)
        period_start = claim_created_at - timedelta(seconds=1)
        period_end = claim_created_at + timedelta(hours=1)

        user_id = connection.execute(
            insert(UsuarioInterno)
            .values(rol=PrincipalRole.SUPERVISOR.value)
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
        principal = make_principal(
            subject=subject,
            role=PrincipalRole.SUPERVISOR,
            now=now,
        )

        claim_id = connection.execute(
            insert(Siniestro)
            .values(
                id_poliza=source.id_poliza,
                id_vehiculo=source.id_vehiculo,
                id_reportante=source.id_reportante,
                fecha_evento=claim_created_at - timedelta(minutes=1),
                ubicacion_evento=f"{MARKER} {token[:8]}",
                tipo_evento=source.tipo_evento,
                descripcion=MARKER,
                danos_aparentes=None,
                estado_actual="reportado",
                canal_origen="api",
                creado_en=claim_created_at,
                version=0,
            )
            .returning(Siniestro.id_siniestro)
        ).scalar_one()

        provider_id = connection.execute(
            insert(Proveedor)
            .values(
                tipo_proveedor="grua",
                nombre=f"Proveedor sintético S6-BE-03 {token[:8]}",
            )
            .returning(Proveedor.id_proveedor)
        ).scalar_one()

        assistance_at = claim_created_at + timedelta(minutes=5)
        assistance_id = connection.execute(
            insert(Asistencia)
            .values(
                id_siniestro=claim_id,
                id_proveedor=provider_id,
                estado_solicitud="aceptada",
                numero_intento=1,
                tipo_asistencia="grua",
                motivo=MARKER,
                referencia_externa=f"S6-METRICS-{token[:12]}",
                creado_en=assistance_at,
                actualizado_en=assistance_at,
            )
            .returning(Asistencia.id_asistencia)
        ).scalar_one()

        decision_at = claim_created_at + timedelta(minutes=20)
        decision_event_id = connection.execute(
            insert(EventoLineaTiempo)
            .values(
                id_siniestro=claim_id,
                id_usuario=user_id,
                tipo_evento="decision_presupuesto_registrada",
                fecha=decision_at,
                detalle={
                    "marcador": MARKER,
                    "decision": "sintetica",
                },
            )
            .returning(EventoLineaTiempo.id_evento)
        ).scalar_one()

        factory = sessionmaker(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        service = GetOperationalMetricsService(
            PostgreSQLOperationalMetricsRepository(factory)
        )
        result = service.execute(
            period_start=period_start,
            period_end=period_end,
            principal=principal,
        )
        by_name = {item.name: item for item in result.indicators}

        first_assistance = by_name[
            IndicatorName.TIEMPO_PRIMERA_ASISTENCIA
        ]
        require(
            first_assistance.availability
            is IndicatorAvailability.DISPONIBLE,
            "Tiempo de asistencia no disponible",
        )
        require(
            first_assistance.value_seconds == 300,
            "Tiempo de asistencia incorrecto",
        )
        require(
            first_assistance.sources
            == ("siniestro.creado_en", "asistencia.creado_en"),
            "Fuentes de asistencia incorrectas",
        )

        first_decision = by_name[IndicatorName.TIEMPO_HASTA_DECISION]
        require(
            first_decision.availability
            is IndicatorAvailability.DISPONIBLE,
            "Tiempo de decisión no disponible",
        )
        require(
            first_decision.value_seconds == 1200,
            "Tiempo de decisión incorrecto",
        )
        require(
            result.source_claim_id == claim_id,
            "Caso fuente no identificado",
        )
        require(
            result.period_start == period_start
            and result.period_end == period_end,
            "Período no conservado",
        )

        for name in (
            IndicatorName.CASOS_SIN_LLAMADAS_ADICIONALES,
            IndicatorName.SATISFACCION_CLIENTE,
            IndicatorName.COSTO_OPERATIVO,
            IndicatorName.PERDIDAS_EVITADAS_FRAUDE,
        ):
            indicator = by_name[name]
            require(
                indicator.availability
                is IndicatorAvailability.NO_DISPONIBLE,
                f"{name.value} no debería estar disponible",
            )
            require(
                indicator.value_seconds is None,
                f"{name.value} fue convertido a cero",
            )
            require(indicator.reason is not None, "Falta explicación")

        print(f"Siniestro fuente: {claim_id}")
        print("Tiempo hasta primera asistencia: 300 segundos — OK")
        print("Tiempo hasta decisión: 1200 segundos — OK")
        print("Período y fuentes conservados: OK")
        print("Indicadores sin fuente: no_disponible — OK")
        print("Ausencia de datos no convertida a cero: OK")

        invalid_principal = make_principal(
            subject=f"s6-metrics-invalid-{token}",
            role=PrincipalRole.SUPERVISOR,
            now=now,
        )
        try:
            service.execute(
                period_start=period_start,
                period_end=period_end,
                principal=invalid_principal,
            )
        except OperationalMetricsError as exc:
            require(
                exc.code == "OPERATIONAL-METRICS-FORBIDDEN",
                "Código de identidad inesperado",
            )
            require(exc.status_code == 403, "HTTP inesperado")
            print("Supervisor sin identidad persistida: HTTP 403 — OK")
        else:
            raise AssertionError("Identidad no persistida obtuvo indicadores")

        operator = make_principal(
            subject=f"s6-metrics-operator-{token}",
            role=PrincipalRole.OPERADOR,
            now=now,
        )
        try:
            service.execute(
                period_start=period_start,
                period_end=period_end,
                principal=operator,
            )
        except OperationalMetricsError as exc:
            require(
                exc.code == "OPERATIONAL-METRICS-FORBIDDEN",
                "Código RBAC inesperado",
            )
            require(exc.status_code == 403, "HTTP RBAC inesperado")
            print("Operador no autorizado: HTTP 403 — OK")
        else:
            raise AssertionError("Operador obtuvo indicadores")

        empty_result = service.execute(
            period_start=claim_created_at + timedelta(days=2),
            period_end=claim_created_at + timedelta(days=3),
            principal=principal,
        )
        require(
            empty_result.source_claim_id is None,
            "Período vacío identificó un caso",
        )
        require(
            empty_result.indicators[0].availability
            is IndicatorAvailability.NO_DISPONIBLE,
            "Período vacío produjo un indicador",
        )
        require(
            empty_result.indicators[0].value_seconds is None,
            "Período vacío se convirtió a cero",
        )
        print("Período sin casos: no_disponible — OK")
        print("S6-BE-03 PostgreSQL: OK")
    finally:
        outer.rollback()
        print("ROLLBACK ejecutado")

with engine.connect() as verification:
    checks = [
        (Siniestro.id_siniestro, claim_id),
        (Proveedor.id_proveedor, provider_id),
        (Asistencia.id_asistencia, assistance_id),
        (EventoLineaTiempo.id_evento, decision_event_id),
        (UsuarioInterno.id_usuario, user_id),
    ]
    for column, value in checks:
        if value is not None:
            require(
                verification.execute(
                    select(column).where(column == value)
                ).scalar_one_or_none()
                is None,
                f"Residuo detectado en {column}",
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

print("Siniestro, asistencia y decisión sintéticos eliminados: OK")
print("Proveedor, identidad y usuario sintéticos eliminados: OK")
print("Limpieza validada: sin registros residuales")
print("VALIDACIÓN FINAL S6-BE-03 COMPLETADA")
engine.dispose()
