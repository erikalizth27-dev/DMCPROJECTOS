from __future__ import annotations

import os
from datetime import date, datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import create_engine, insert, select, update
from sqlalchemy.orm import sessionmaker

from siniestro_facil.application.decide_budget import (
    BudgetDecisionError,
    DecideBudgetCommand,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.enums import EstadoSiniestro
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal
from siniestro_facil.domain.inspection_budget import BudgetStatus
from siniestro_facil.persistence.inspection_budget_repository import (
    PostgreSQLBudgetDecisionRepository,
)
from siniestro_facil.persistence.models import (
    AsignacionSiniestro,
    Autorizacion,
    CambioPresupuesto,
    EventoLineaTiempo,
    IdentidadActor,
    Inspeccion,
    Presupuesto,
    Proveedor,
    Siniestro,
    SolicitudDecisionPresupuestoIdempotente,
    UsuarioInterno,
)

MARKER = "Validación sintética S4-BE-03"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def make_principal(
    *, subject: str, role: PrincipalRole, now: datetime
) -> AuthenticatedPrincipal:
    return AuthenticatedPrincipal(
        subject=subject,
        tenant_id="tenant-s4-validation",
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
created: dict[str, list[int]] = {
    "users": [], "assignments": [], "providers": [], "inspections": [],
    "budgets": [], "authorizations": [], "changes": [], "audits": [],
}
subjects: list[str] = []
original: tuple[int, str, int] | None = None
keys = ["s4-decision-observe-0001", "s4-decision-authorize-0001"]

with engine.connect() as connection:
    outer = connection.begin()
    try:
        original = connection.execute(
            select(
                Siniestro.id_siniestro,
                Siniestro.estado_actual,
                Siniestro.version,
            ).order_by(Siniestro.id_siniestro).limit(1)
        ).one_or_none()
        require(original is not None, "No existe siniestro para validar")
        claim_id, original_state, original_version = original
        now = datetime.now(timezone.utc)

        provider_id = connection.execute(
            insert(Proveedor).values(
                tipo_proveedor="taller", nombre="Taller sintético S4-BE-03"
            ).returning(Proveedor.id_proveedor)
        ).scalar_one()
        created["providers"].append(provider_id)
        inspection_id = connection.execute(
            insert(Inspeccion).values(
                id_siniestro=claim_id, fecha_programada=now
            ).returning(Inspeccion.id_inspeccion)
        ).scalar_one()
        created["inspections"].append(inspection_id)

        budget_ids = []
        for diagnosis in ("Presupuesto para observar", "Presupuesto para autorizar"):
            budget_id = connection.execute(
                insert(Presupuesto).values(
                    id_siniestro=claim_id,
                    id_inspeccion=inspection_id,
                    id_proveedor=provider_id,
                    diagnostico=diagnosis,
                    vigencia_desde=date(2026, 9, 2),
                    vigencia_hasta=date(2026, 9, 17),
                    estado=BudgetStatus.RECEIVED.value,
                ).returning(Presupuesto.id_presupuesto)
            ).scalar_one()
            budget_ids.append(budget_id)
            created["budgets"].append(budget_id)

        principals = {}
        for role in (PrincipalRole.OPERADOR, PrincipalRole.SUPERVISOR):
            user_id = connection.execute(
                insert(UsuarioInterno).values(rol=role.value)
                .returning(UsuarioInterno.id_usuario)
            ).scalar_one()
            created["users"].append(user_id)
            subject = f"s4-decision-{role.value}-{uuid4().hex}"
            subjects.append(subject)
            connection.execute(
                insert(IdentidadActor).values(
                    subject=subject,
                    tenant_id="tenant-s4-validation",
                    actor_type=ActorType.INTERNO.value,
                    id_usuario=user_id,
                )
            )
            if role is PrincipalRole.OPERADOR:
                assignment_id = connection.execute(
                    insert(AsignacionSiniestro).values(
                        id_siniestro=claim_id,
                        id_usuario=user_id,
                        motivo=MARKER,
                        asignado_en=now,
                    ).returning(AsignacionSiniestro.id_asignacion)
                ).scalar_one()
                created["assignments"].append(assignment_id)
            principals[role] = make_principal(
                subject=subject, role=role, now=now
            )

        connection.execute(
            update(Siniestro).where(Siniestro.id_siniestro == claim_id)
            .values(estado_actual=EstadoSiniestro.PRESUPUESTO_RECIBIDO.value)
        )
        factory = sessionmaker(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        repository = PostgreSQLBudgetDecisionRepository(factory)

        observe = DecideBudgetCommand(
            claim_id=claim_id,
            budget_id=budget_ids[0],
            target=BudgetStatus.OBSERVED,
            reason=f"{MARKER} — observación",
            expected_version=original_version,
            idempotency_key=keys[0],
            fingerprint="a" * 64,
        )
        observed = repository.decide(
            observe, principals[PrincipalRole.OPERADOR]
        )
        created["changes"].append(observed.decision_id)
        require(observed.current_state is EstadoSiniestro.OBSERVADO, "Estado")
        require(observed.version == original_version + 1, "Versión")
        print("Operador asignado — observación: OK")

        repeated = repository.decide(
            observe, principals[PrincipalRole.OPERADOR]
        )
        require(repeated == observed, "Repetición no idempotente")
        print("Repetición idempotente: OK")
        try:
            repository.decide(
                DecideBudgetCommand(
                    claim_id=observe.claim_id,
                    budget_id=observe.budget_id,
                    target=observe.target,
                    reason="Contenido diferente",
                    expected_version=observe.expected_version,
                    idempotency_key=observe.idempotency_key,
                    fingerprint="b" * 64,
                ),
                principals[PrincipalRole.OPERADOR],
            )
        except BudgetDecisionError as exc:
            require(exc.code == "IDEMPOTENCY-CONFLICT", "Código inesperado")
            print("Conflicto idempotente: HTTP 409 — OK")
        else:
            raise AssertionError("No se detectó conflicto idempotente")

        authorize = DecideBudgetCommand(
            claim_id=claim_id,
            budget_id=budget_ids[1],
            target=BudgetStatus.AUTHORIZED,
            reason=f"{MARKER} — autorización",
            expected_version=observed.version,
            idempotency_key=keys[1],
            fingerprint="c" * 64,
        )
        authorized = repository.decide(
            authorize, principals[PrincipalRole.SUPERVISOR]
        )
        created["changes"].append(authorized.decision_id)
        require(authorized.current_state is EstadoSiniestro.AUTORIZADO, "Estado")
        require(authorized.version == original_version + 2, "Versión")
        print("Supervisor — autorización: OK")

        for change_id in created["changes"]:
            row = connection.execute(
                select(
                    CambioPresupuesto.id_autorizacion,
                    CambioPresupuesto.tipo_cambio,
                ).where(CambioPresupuesto.id_cambio == change_id)
            ).one_or_none()
            require(row is not None, "Cambio no persistido")
            created["authorizations"].append(row.id_autorizacion)
        audit_ids = connection.execute(
            select(EventoLineaTiempo.id_evento).where(
                EventoLineaTiempo.id_siniestro == claim_id,
                EventoLineaTiempo.tipo_evento
                == "decision_presupuesto_registrada",
                EventoLineaTiempo.detalle["justificacion"].as_string().like(
                    f"{MARKER}%"
                ),
            )
        ).scalars().all()
        created["audits"].extend(audit_ids)
        require(len(audit_ids) == 2, "Auditoría incompleta")
        require(
            connection.execute(
                select(SolicitudDecisionPresupuestoIdempotente.clave).where(
                    SolicitudDecisionPresupuestoIdempotente.clave.in_(keys)
                )
            ).scalars().all().__len__() == 2,
            "Idempotencia incompleta",
        )
        print("Autorizaciones y cambios formales: OK")
        print("Auditoría atómica: OK")
        print("S4-BE-03 PostgreSQL: OK")
    finally:
        outer.rollback()
        print("ROLLBACK ejecutado")

require(original is not None, "No se seleccionó siniestro")
claim_id, original_state, original_version = original
with engine.connect() as verification:
    state, version = verification.execute(
        select(Siniestro.estado_actual, Siniestro.version).where(
            Siniestro.id_siniestro == claim_id
        )
    ).one()
    require(state == original_state, "Estado residual")
    require(version == original_version, "Versión residual")
    model_checks = [
        (Presupuesto.id_presupuesto, created["budgets"]),
        (Inspeccion.id_inspeccion, created["inspections"]),
        (CambioPresupuesto.id_cambio, created["changes"]),
        (Autorizacion.id_autorizacion, created["authorizations"]),
        (EventoLineaTiempo.id_evento, created["audits"]),
        (Proveedor.id_proveedor, created["providers"]),
        (UsuarioInterno.id_usuario, created["users"]),
        (AsignacionSiniestro.id_asignacion, created["assignments"]),
    ]
    for column, values in model_checks:
        if values:
            require(
                not verification.execute(
                    select(column).where(column.in_(values))
                ).scalars().all(),
                f"Residuo detectado en {column}",
            )
    require(
        not verification.execute(
            select(SolicitudDecisionPresupuestoIdempotente.clave).where(
                SolicitudDecisionPresupuestoIdempotente.clave.in_(keys)
            )
        ).scalars().all(),
        "Idempotencia residual",
    )
    require(
        not verification.execute(
            select(IdentidadActor.subject).where(
                IdentidadActor.subject.in_(subjects)
            )
        ).scalars().all(),
        "Identidad residual",
    )

print("Estado y versión restaurados: OK")
print("Decisiones, cambios y autorizaciones eliminados: OK")
print("Auditoría e idempotencia eliminadas: OK")
print("Datos sintéticos eliminados: OK")
print("Limpieza validada: sin registros residuales")
print("VALIDACIÓN FINAL S4-BE-03 COMPLETADA")
engine.dispose()
