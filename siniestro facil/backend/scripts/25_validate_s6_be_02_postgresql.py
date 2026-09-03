from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import create_engine, func, insert, select
from sqlalchemy.orm import sessionmaker

from siniestro_facil.application.get_claim_timeline import (
    ClaimTimelineError,
    GetClaimTimelineService,
)
from siniestro_facil.domain.audit import AuditDetailLevel
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal
from siniestro_facil.persistence.claim_timeline_repository import (
    PostgreSQLClaimTimelineRepository,
)
from siniestro_facil.persistence.models import (
    AsignacionSiniestro,
    EventoLineaTiempo,
    IdentidadActor,
    Siniestro,
    UsuarioInterno,
)


TENANT = "tenant-s6-timeline-validation"
MARKER = "Validación sintética S6-BE-02"


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
claim_id: int | None = None
subjects: list[str] = []
created: dict[str, list[int]] = {
    "users": [],
    "assignments": [],
    "events": [],
    "access_audits": [],
}

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

        principals: dict[str, AuthenticatedPrincipal] = {}
        role_specs = (
            ("assigned", PrincipalRole.OPERADOR, True),
            ("unassigned", PrincipalRole.OPERADOR, False),
            ("supervisor", PrincipalRole.SUPERVISOR, False),
        )
        for label, role, assigned in role_specs:
            user_id = connection.execute(
                insert(UsuarioInterno)
                .values(rol=role.value)
                .returning(UsuarioInterno.id_usuario)
            ).scalar_one()
            created["users"].append(user_id)
            subject = f"s6-timeline-{label}-{token}"
            subjects.append(subject)
            connection.execute(
                insert(IdentidadActor).values(
                    subject=subject,
                    tenant_id=TENANT,
                    actor_type=ActorType.INTERNO.value,
                    id_usuario=user_id,
                )
            )
            if assigned:
                assignment_id = connection.execute(
                    insert(AsignacionSiniestro)
                    .values(
                        id_siniestro=claim_id,
                        id_usuario=user_id,
                        motivo=MARKER,
                        asignado_en=now,
                    )
                    .returning(AsignacionSiniestro.id_asignacion)
                ).scalar_one()
                created["assignments"].append(assignment_id)
            principals[label] = make_principal(
                subject=subject,
                role=role,
                now=now,
            )

        normal_id = connection.execute(
            insert(EventoLineaTiempo)
            .values(
                id_siniestro=claim_id,
                id_usuario=created["users"][0],
                tipo_evento="pago_preparado",
                fecha=now,
                detalle={
                    "marcador": MARKER,
                    "monto": "1250.00",
                    "simulado": True,
                },
            )
            .returning(EventoLineaTiempo.id_evento)
        ).scalar_one()
        sensitive_id = connection.execute(
            insert(EventoLineaTiempo)
            .values(
                id_siniestro=claim_id,
                id_usuario=created["users"][2],
                tipo_evento="alerta_fraude_revisada",
                fecha=now + timedelta(seconds=1),
                detalle={
                    "marcador": MARKER,
                    "explicacion": "Detalle sintético reservado",
                },
            )
            .returning(EventoLineaTiempo.id_evento)
        ).scalar_one()
        created["events"].extend((normal_id, sensitive_id))

        factory = sessionmaker(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        service = GetClaimTimelineService(
            PostgreSQLClaimTimelineRepository(factory)
        )

        operator_result = service.execute(
            claim_id,
            principals["assigned"],
            after_event_id=normal_id - 1,
        )
        selected = {
            event.event_id: event for event in operator_result.events
            if event.event_id in {normal_id, sensitive_id}
        }
        require(len(selected) == 2, "Línea de tiempo incompleta")
        require(
            selected[normal_id].detail["monto"] == "1250.00",
            "Detalle operativo no disponible",
        )
        require(
            selected[sensitive_id].detail
            == {"resumen": "Información sensible restringida"},
            "Detalle sensible no fue redactado",
        )
        require(
            operator_result.detail_level is AuditDetailLevel.OPERATIVO,
            "Nivel operativo incorrecto",
        )
        print(f"Siniestro probado: {claim_id}")
        print("Operador asignado — alcance validado: OK")
        print("Detalle operativo visible: OK")
        print("Detalle sensible redactado: OK")

        try:
            service.execute(claim_id, principals["unassigned"])
        except ClaimTimelineError as exc:
            require(
                exc.code == "CLAIM-TIMELINE-NOT-FOUND",
                "Código privado inesperado",
            )
            require(exc.status_code == 404, "HTTP privado inesperado")
            print("Operador no asignado — respuesta privada HTTP 404: OK")
        else:
            raise AssertionError("Operador no asignado obtuvo acceso")

        first_page = service.execute(
            claim_id,
            principals["assigned"],
            after_event_id=normal_id - 1,
            page_size=1,
        )
        require(
            [event.event_id for event in first_page.events] == [normal_id],
            "Primera página incorrecta",
        )
        require(
            first_page.next_cursor == normal_id,
            "Cursor siguiente incorrecto",
        )
        second_page = service.execute(
            claim_id,
            principals["assigned"],
            after_event_id=first_page.next_cursor,
            page_size=1,
        )
        require(
            [event.event_id for event in second_page.events]
            == [sensitive_id],
            "Segunda página incorrecta",
        )
        require(second_page.next_cursor is None, "Cursor final incorrecto")
        print("Paginación estable por cursor: OK")

        max_event_before_access = connection.execute(
            select(func.max(EventoLineaTiempo.id_evento))
        ).scalar_one()
        supervisor_result = service.execute(
            claim_id,
            principals["supervisor"],
            after_event_id=normal_id - 1,
        )
        supervisor_events = {
            event.event_id: event for event in supervisor_result.events
            if event.event_id in {normal_id, sensitive_id}
        }
        require(
            supervisor_events[sensitive_id].detail["explicacion"]
            == "Detalle sintético reservado",
            "Supervisor no recibió detalle completo",
        )
        require(
            supervisor_result.detail_level is AuditDetailLevel.COMPLETO,
            "Nivel supervisor incorrecto",
        )

        access_rows = connection.execute(
            select(EventoLineaTiempo).where(
                EventoLineaTiempo.id_evento > max_event_before_access,
                EventoLineaTiempo.id_siniestro == claim_id,
                EventoLineaTiempo.tipo_evento
                == "consulta_auditoria_sensible",
            )
        ).scalars().all()
        require(len(access_rows) == 1, "Acceso sensible no auditado")
        access = access_rows[0]
        created["access_audits"].append(access.id_evento)
        require(
            sensitive_id in access.detalle["eventos_consultados"],
            "Evento sensible no referenciado en auditoría",
        )
        require(
            access.id_usuario == created["users"][2],
            "Actor de consulta sensible incorrecto",
        )
        print("Supervisor — detalle completo: OK")
        print("Consulta sensible auditada con identidad: OK")
        print("S6-BE-02 PostgreSQL: OK")
    finally:
        outer.rollback()
        print("ROLLBACK ejecutado")

require(claim_id is not None, "No se seleccionó siniestro")
with engine.connect() as verification:
    checks = [
        (
            EventoLineaTiempo.id_evento,
            created["events"] + created["access_audits"],
        ),
        (AsignacionSiniestro.id_asignacion, created["assignments"]),
        (UsuarioInterno.id_usuario, created["users"]),
    ]
    for column, values in checks:
        if values:
            require(
                not verification.execute(
                    select(column).where(column.in_(values))
                ).scalars().all(),
                f"Residuo detectado en {column}",
            )
    require(
        not verification.execute(
            select(IdentidadActor.subject).where(
                IdentidadActor.subject.in_(subjects)
            )
        ).scalars().all(),
        "Identidad residual",
    )

print("Eventos y auditoría sintéticos eliminados: OK")
print("Asignación, identidades y usuarios eliminados: OK")
print("Limpieza validada: sin registros residuales")
print("VALIDACIÓN FINAL S6-BE-02 COMPLETADA")
engine.dispose()
