from __future__ import annotations

import os
from datetime import date, datetime, timezone
from uuid import uuid4

from sqlalchemy import create_engine, insert, select, update
from sqlalchemy.orm import sessionmaker

from siniestro_facil.application.submit_budget import (
    BudgetSubmissionError,
    SubmitBudgetCommand,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.enums import EstadoSiniestro
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal
from siniestro_facil.persistence.inspection_budget_repository import (
    PostgreSQLBudgetSubmissionRepository,
)
from siniestro_facil.persistence.models import (
    EventoLineaTiempo,
    IdentidadActor,
    Inspeccion,
    Presupuesto,
    Proveedor,
    Siniestro,
    SolicitudPresupuestoIdempotente,
)

MARKER = "Validación sintética S4-BE-02"
IDEMPOTENCY_KEY = "s4-budget-validation-0001"
FINGERPRINT = "a" * 64


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL no configurada")

engine = create_engine(database_url, pool_pre_ping=True)
claim_id: int | None = None
provider_id: int | None = None
inspection_id: int | None = None
budget_id: int | None = None
audit_id: int | None = None
subject: str | None = None
original_state: str | None = None
original_version: int | None = None

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

        provider_id = connection.execute(
            insert(Proveedor)
            .values(
                tipo_proveedor="taller",
                nombre="Taller sintético S4-BE-02",
            )
            .returning(Proveedor.id_proveedor)
        ).scalar_one()
        subject = f"s4-budget-validation-{uuid4().hex}"
        connection.execute(
            insert(IdentidadActor).values(
                subject=subject,
                tenant_id="tenant-s4-validation",
                actor_type=ActorType.PROVEEDOR.value,
                id_proveedor=provider_id,
            )
        )
        inspection_id = connection.execute(
            insert(Inspeccion)
            .values(
                id_siniestro=claim_id,
                fecha_programada=now,
            )
            .returning(Inspeccion.id_inspeccion)
        ).scalar_one()
        connection.execute(
            update(Siniestro)
            .where(Siniestro.id_siniestro == claim_id)
            .values(
                estado_actual=EstadoSiniestro.INSPECCION_PROGRAMADA.value
            )
        )

        principal = AuthenticatedPrincipal(
            subject=subject,
            tenant_id="tenant-s4-validation",
            actor_type=ActorType.PROVEEDOR,
            role=PrincipalRole.TALLER,
            issued_at=now,
            expires_at=now,
            authenticated_at=now,
        )
        factory = sessionmaker(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        repository = PostgreSQLBudgetSubmissionRepository(factory)
        command = SubmitBudgetCommand(
            claim_id=claim_id,
            inspection_id=inspection_id,
            diagnosis=MARKER,
            presented_on=date(2026, 9, 2),
            expected_version=original_version,
            idempotency_key=IDEMPOTENCY_KEY,
            fingerprint=FINGERPRINT,
        )

        result = repository.submit(command, principal)
        budget_id = result.id
        require(result.inspection_id == inspection_id, "Vínculo incorrecto")
        require(result.provider_id == provider_id, "Proveedor incorrecto")
        require(result.valid_until == date(2026, 9, 17), "Vigencia incorrecta")
        require(
            result.current_state is EstadoSiniestro.PRESUPUESTO_RECIBIDO,
            "Estado incorrecto",
        )
        require(result.version == original_version + 1, "Versión incorrecta")
        print(f"Siniestro probado: {claim_id}")
        print(f"Inspección probada: {inspection_id}")
        print(f"Proveedor sintético: {provider_id}")
        print(f"Presupuesto registrado: {budget_id}")
        print("Vigencia de 15 días: OK")

        stored = connection.execute(
            select(Presupuesto.id_presupuesto).where(
                Presupuesto.id_presupuesto == budget_id,
                Presupuesto.id_inspeccion == inspection_id,
                Presupuesto.id_proveedor == provider_id,
            )
        ).scalar_one_or_none()
        require(stored is not None, "Presupuesto no persistido")
        request = connection.execute(
            select(SolicitudPresupuestoIdempotente.id_presupuesto).where(
                SolicitudPresupuestoIdempotente.clave == IDEMPOTENCY_KEY
            )
        ).scalar_one_or_none()
        require(request == budget_id, "Idempotencia no persistida")
        audit_id = connection.execute(
            select(EventoLineaTiempo.id_evento).where(
                EventoLineaTiempo.id_siniestro == claim_id,
                EventoLineaTiempo.tipo_evento == "presupuesto_presentado",
                EventoLineaTiempo.detalle["id_presupuesto"].as_integer()
                == budget_id,
            )
        ).scalar_one_or_none()
        require(audit_id is not None, "Auditoría no persistida")
        print("Persistencia y vínculo con inspección: OK")
        print("Auditoría atómica: OK")
        print("Idempotencia persistente: OK")

        repeated = repository.submit(command, principal)
        require(repeated == result, "La repetición cambió el resultado")
        print("Repetición idempotente: OK")

        conflicting = SubmitBudgetCommand(
            claim_id=command.claim_id,
            inspection_id=command.inspection_id,
            diagnosis="Contenido diferente",
            presented_on=command.presented_on,
            expected_version=command.expected_version,
            idempotency_key=command.idempotency_key,
            fingerprint="b" * 64,
        )
        try:
            repository.submit(conflicting, principal)
        except BudgetSubmissionError as exc:
            require(exc.code == "IDEMPOTENCY-CONFLICT", "Código inesperado")
            require(exc.status_code == 409, "HTTP inesperado")
            print("Conflicto idempotente: HTTP 409 — OK")
        else:
            raise AssertionError("No se detectó conflicto idempotente")

        print("S4-BE-02 PostgreSQL: OK")
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
    checks = [
        (Presupuesto.id_presupuesto, budget_id, "Presupuesto residual"),
        (Inspeccion.id_inspeccion, inspection_id, "Inspección residual"),
        (EventoLineaTiempo.id_evento, audit_id, "Auditoría residual"),
        (Proveedor.id_proveedor, provider_id, "Proveedor residual"),
    ]
    for column, value, message in checks:
        if value is not None:
            require(
                verification.execute(
                    select(column).where(column == value)
                ).scalar_one_or_none()
                is None,
                message,
            )
    require(
        verification.execute(
            select(SolicitudPresupuestoIdempotente.clave).where(
                SolicitudPresupuestoIdempotente.clave == IDEMPOTENCY_KEY
            )
        ).scalar_one_or_none()
        is None,
        "Idempotencia residual",
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

print("Estado y versión restaurados: OK")
print("Presupuesto e inspección sintéticos eliminados: OK")
print("Auditoría e idempotencia sintéticas eliminadas: OK")
print("Proveedor e identidad sintéticos eliminados: OK")
print("Limpieza validada: sin registros residuales")
print("VALIDACIÓN FINAL S4-BE-02 COMPLETADA")
engine.dispose()
