from __future__ import annotations

import os
from uuid import uuid4
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, insert, select, update
from sqlalchemy.orm import sessionmaker

from siniestro_facil.application.schedule_inspection import (
    InspectionSchedulingError,
    ScheduleInspectionCommand,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.enums import EstadoSiniestro
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal
from siniestro_facil.persistence.inspection_budget_repository import (
    PostgreSQLInspectionSchedulingRepository,
)
from siniestro_facil.persistence.models import (
    AsignacionSiniestro,
    EventoLineaTiempo,
    IdentidadActor,
    Inspeccion,
    Siniestro,
    UsuarioInterno,
)

MARKER = "Validación sintética S4-BE-01"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL no configurada")

engine = create_engine(database_url, pool_pre_ping=True)
inspection_id: int | None = None
audit_id: int | None = None
claim_id: int | None = None
original_state: str | None = None
original_version: int | None = None
user_id: int | None = None
assignment_id: int | None = None
subject: str | None = None

with engine.connect() as connection:
    outer_transaction = connection.begin()
    try:
        claim_row = connection.execute(
            select(
                Siniestro.id_siniestro,
                Siniestro.estado_actual,
                Siniestro.version,
            )
            .order_by(Siniestro.id_siniestro)
            .limit(1)
        ).one_or_none()
        require(claim_row is not None, "No existe un siniestro para validar")
        claim_id, original_state, original_version = claim_row
        now = datetime.now(timezone.utc)

        user_id = connection.execute(
            insert(UsuarioInterno)
            .values(rol=PrincipalRole.OPERADOR.value)
            .returning(UsuarioInterno.id_usuario)
        ).scalar_one()
        subject = f"s4-be-01-validation-{uuid4().hex}"
        tenant_id = "tenant-s4-validation"
        connection.execute(
            insert(IdentidadActor).values(
                subject=subject,
                tenant_id=tenant_id,
                actor_type=ActorType.INTERNO.value,
                id_usuario=user_id,
            )
        )
        assignment_id = connection.execute(
            insert(AsignacionSiniestro)
            .values(
                id_siniestro=claim_id,
                id_usuario=user_id,
                motivo=MARKER,
                asignado_en=now,
                finalizado_en=None,
            )
            .returning(AsignacionSiniestro.id_asignacion)
        ).scalar_one()

        connection.execute(
            update(Siniestro)
            .where(Siniestro.id_siniestro == claim_id)
            .values(estado_actual=EstadoSiniestro.EN_EVALUACION.value)
        )

        principal = AuthenticatedPrincipal(
            subject=subject,
            tenant_id=tenant_id,
            actor_type=ActorType.INTERNO,
            role=PrincipalRole.OPERADOR,
            issued_at=now - timedelta(minutes=1),
            expires_at=now + timedelta(hours=1),
            authenticated_at=now - timedelta(minutes=1),
        )
        factory = sessionmaker(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        repository = PostgreSQLInspectionSchedulingRepository(factory)
        command = ScheduleInspectionCommand(
            claim_id=claim_id,
            scheduled_at=now + timedelta(days=1),
            expected_version=original_version,
            reason=MARKER,
        )

        result = repository.schedule(command, principal)
        inspection_id = result.id
        require(
            result.current_state is EstadoSiniestro.INSPECCION_PROGRAMADA,
            "El estado no cambió a inspeccion_programada",
        )
        require(
            result.version == original_version + 1,
            "La versión no fue incrementada",
        )
        print(f"Siniestro probado: {claim_id}")
        print(f"Inspección registrada: {inspection_id}")
        print(
            f"Estado: {EstadoSiniestro.EN_EVALUACION.value} -> "
            f"{result.current_state.value}"
        )
        print(f"Versión: {original_version} -> {result.version}")

        inspection = connection.execute(
            select(Inspeccion.id_inspeccion).where(
                Inspeccion.id_inspeccion == inspection_id
            )
        ).scalar_one_or_none()
        require(inspection is not None, "La inspección no fue persistida")
        audit = connection.execute(
            select(EventoLineaTiempo.id_evento).where(
                EventoLineaTiempo.id_siniestro == claim_id,
                EventoLineaTiempo.tipo_evento == "inspeccion_programada",
                EventoLineaTiempo.detalle["motivo"].as_string() == MARKER,
            )
        ).scalar_one_or_none()
        require(audit is not None, "La auditoría no fue persistida")
        audit_id = audit
        print("Persistencia de inspección: OK")
        print("Auditoría atómica: OK")

        visible = repository.get(claim_id, inspection_id, principal)
        require(visible is not None, "La inspección no puede consultarse")
        require(visible.version == result.version, "Consulta con versión incorrecta")
        print("Consulta con alcance: OK")

        try:
            repository.schedule(command, principal)
        except InspectionSchedulingError as exc:
            require(exc.code == "STATE-VERSION-CONFLICT", "Código inesperado")
            require(exc.status_code == 409, "HTTP inesperado")
            print("Conflicto de versión: HTTP 409 — OK")
        else:
            raise AssertionError("No se rechazó la versión desactualizada")

        print("S4-BE-01 PostgreSQL: OK")
    finally:
        outer_transaction.rollback()
        print("ROLLBACK ejecutado")

require(claim_id is not None, "No se seleccionó siniestro")
with engine.connect() as verification:
    restored_state, restored_version = verification.execute(
        select(Siniestro.estado_actual, Siniestro.version).where(
            Siniestro.id_siniestro == claim_id
        )
    ).one()
    require(restored_state == original_state, "Estado residual")
    require(restored_version == original_version, "Versión residual")
    if inspection_id is not None:
        require(
            verification.execute(
                select(Inspeccion).where(
                    Inspeccion.id_inspeccion == inspection_id
                )
            ).scalar_one_or_none()
            is None,
            "Inspección residual",
        )
    if audit_id is not None:
        require(
            verification.execute(
                select(EventoLineaTiempo.id_evento).where(
                    EventoLineaTiempo.id_evento == audit_id
                )
            ).scalar_one_or_none()
            is None,
            "Auditoría residual",
        )
    if assignment_id is not None:
        require(
            verification.execute(
                select(AsignacionSiniestro.id_asignacion).where(
                    AsignacionSiniestro.id_asignacion == assignment_id
                )
            ).scalar_one_or_none()
            is None,
            "Asignación residual",
        )
    if subject is not None:
        require(
            verification.execute(
                select(IdentidadActor.subject).where(
                    IdentidadActor.subject == subject
                )
            ).scalar_one_or_none()
            is None,
            "Identidad residual",
        )
    if user_id is not None:
        require(
            verification.execute(
                select(UsuarioInterno.id_usuario).where(
                    UsuarioInterno.id_usuario == user_id
                )
            ).scalar_one_or_none()
            is None,
            "Usuario residual",
        )

print("Estado y versión restaurados: OK")
print("Inspección sintética eliminada: OK")
print("Auditoría sintética eliminada: OK")
print("Asignación sintética eliminada: OK")
print("Identidad y usuario sintéticos eliminados: OK")
print("Limpieza validada: sin registros residuales")
print("VALIDACIÓN FINAL S4-BE-01 COMPLETADA")
engine.dispose()
