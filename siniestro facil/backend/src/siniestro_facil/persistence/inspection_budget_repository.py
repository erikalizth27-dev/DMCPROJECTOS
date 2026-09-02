from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import exists, select
from sqlalchemy.orm import Session, sessionmaker

from siniestro_facil.application.schedule_inspection import (
    InspectionSchedulingError,
    ScheduleInspectionCommand,
    ScheduledInspection,
)
from siniestro_facil.application.inspection_budget_contracts import (
    BudgetRecord,
    ClaimInspectionContext,
    InspectionRecord,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.enums import EstadoSiniestro, RolUsuario
from siniestro_facil.domain.identity import AuthenticatedPrincipal
from siniestro_facil.domain.inspection_budget import BudgetStatus
from siniestro_facil.domain.state_machine import (
    SolicitudTransicion,
    TransicionNoPermitida,
    validar_transicion,
)
from siniestro_facil.persistence.models import (
    AsignacionSiniestro,
    EventoLineaTiempo,
    IdentidadActor,
    Inspeccion,
    Presupuesto,
    Siniestro,
    UsuarioInterno,
)


class PostgreSQLInspectionBudgetRepository:
    """Fundación de lectura y alcance para los incrementos de Sprint 4."""

    def __init__(self, factory: sessionmaker[Session]) -> None:
        self._factory = factory

    @staticmethod
    def _internal_identity_in_scope(
        session: Session,
        claim_id: int,
        principal: AuthenticatedPrincipal,
    ) -> IdentidadActor | None:
        identity = session.get(
            IdentidadActor,
            (principal.subject, principal.tenant_id),
        )
        if (
            identity is None
            or identity.actor_type != principal.actor_type.value
            or identity.id_usuario is None
        ):
            return None
        user = session.get(UsuarioInterno, identity.id_usuario)
        if user is None or user.rol != principal.role.value:
            return None
        if principal.role is PrincipalRole.SUPERVISOR:
            return identity
        if principal.role not in {
            PrincipalRole.OPERADOR,
            PrincipalRole.AJUSTADOR,
        }:
            return None
        assigned = session.scalar(
            select(
                exists().where(
                    AsignacionSiniestro.id_siniestro == claim_id,
                    AsignacionSiniestro.id_usuario == identity.id_usuario,
                    AsignacionSiniestro.finalizado_en.is_(None),
                )
            )
        )
        return identity if assigned else None

    @staticmethod
    def _inspection_record(row: Inspeccion) -> InspectionRecord:
        return InspectionRecord(
            id=row.id_inspeccion,
            claim_id=row.id_siniestro,
            scheduled_at=row.fecha_programada,
        )

    @staticmethod
    def _budget_record(row: Presupuesto) -> BudgetRecord:
        return BudgetRecord(
            id=row.id_presupuesto,
            claim_id=row.id_siniestro,
            provider_id=row.id_proveedor,
            diagnosis=row.diagnostico,
            valid_from=row.vigencia_desde,
            valid_until=row.vigencia_hasta,
            status=BudgetStatus(row.estado),
        )

    def find_claim_context(
        self,
        claim_id: int,
        principal: AuthenticatedPrincipal,
    ) -> ClaimInspectionContext | None:
        with self._factory() as session:
            if (
                self._internal_identity_in_scope(
                    session,
                    claim_id,
                    principal,
                )
                is None
            ):
                return None
            claim = session.get(Siniestro, claim_id)
            if claim is None:
                return None
            return ClaimInspectionContext(
                claim_id=claim.id_siniestro,
                current_state=claim.estado_actual,
                version=claim.version,
            )

    def find_inspection(
        self,
        claim_id: int,
        inspection_id: int,
        principal: AuthenticatedPrincipal,
    ) -> InspectionRecord | None:
        with self._factory() as session:
            if (
                self._internal_identity_in_scope(
                    session,
                    claim_id,
                    principal,
                )
                is None
            ):
                return None
            row = session.get(Inspeccion, inspection_id)
            if row is None or row.id_siniestro != claim_id:
                return None
            return self._inspection_record(row)

    def find_budget(
        self,
        claim_id: int,
        budget_id: int,
        principal: AuthenticatedPrincipal,
    ) -> BudgetRecord | None:
        with self._factory() as session:
            identity = session.get(
                IdentidadActor,
                (principal.subject, principal.tenant_id),
            )
            if identity is None or identity.actor_type != principal.actor_type.value:
                return None

            if principal.role is PrincipalRole.TALLER:
                if identity.id_proveedor is None:
                    return None
                row = session.get(Presupuesto, budget_id)
                if (
                    row is None
                    or row.id_siniestro != claim_id
                    or row.id_proveedor != identity.id_proveedor
                ):
                    return None
                return self._budget_record(row)

            if (
                self._internal_identity_in_scope(
                    session,
                    claim_id,
                    principal,
                )
                is None
            ):
                return None
            row = session.get(Presupuesto, budget_id)
            if row is None or row.id_siniestro != claim_id:
                return None
            return self._budget_record(row)


class PostgreSQLInspectionSchedulingRepository:
    """Programa y consulta inspecciones con alcance y auditoría atómica."""

    def __init__(self, factory: sessionmaker[Session]) -> None:
        self._factory = factory

    def schedule(
        self,
        command: ScheduleInspectionCommand,
        principal: AuthenticatedPrincipal,
    ) -> ScheduledInspection:
        with self._factory() as session, session.begin():
            identity = PostgreSQLInspectionBudgetRepository._internal_identity_in_scope(
                session,
                command.claim_id,
                principal,
            )
            if identity is None:
                raise InspectionSchedulingError(
                    "INSPECTION-NOT-FOUND",
                    "Siniestro no encontrado",
                    404,
                )

            claim = session.execute(
                select(Siniestro)
                .where(Siniestro.id_siniestro == command.claim_id)
                .with_for_update()
            ).scalar_one_or_none()
            if claim is None:
                raise InspectionSchedulingError(
                    "INSPECTION-NOT-FOUND",
                    "Siniestro no encontrado",
                    404,
                )
            if claim.version != command.expected_version:
                raise InspectionSchedulingError(
                    "STATE-VERSION-CONFLICT",
                    "La versión del siniestro está desactualizada",
                    409,
                )

            try:
                origin = EstadoSiniestro(claim.estado_actual)
                validar_transicion(
                    SolicitudTransicion(
                        origen=origin,
                        destino=EstadoSiniestro.INSPECCION_PROGRAMADA,
                        rol=RolUsuario(principal.role.value),
                        motivo=command.reason,
                    )
                )
            except (ValueError, TransicionNoPermitida) as exc:
                raise InspectionSchedulingError(
                    "INVALID-TRANSITION",
                    str(exc),
                    409,
                ) from exc

            inspection = Inspeccion(
                id_siniestro=claim.id_siniestro,
                fecha_programada=command.scheduled_at,
            )
            session.add(inspection)
            previous_state = claim.estado_actual
            claim.estado_actual = EstadoSiniestro.INSPECCION_PROGRAMADA.value
            claim.version += 1
            session.add(
                EventoLineaTiempo(
                    id_siniestro=claim.id_siniestro,
                    id_usuario=identity.id_usuario,
                    tipo_evento="inspeccion_programada",
                    fecha=datetime.now(timezone.utc),
                    detalle={
                        "estado_anterior": previous_state,
                        "estado_nuevo": claim.estado_actual,
                        "fecha_programada": command.scheduled_at.isoformat(),
                        "motivo": command.reason.strip(),
                        "version_anterior": command.expected_version,
                        "version_nueva": claim.version,
                        "subject": principal.subject,
                        "tenant_id": principal.tenant_id,
                    },
                )
            )
            session.flush()
            return ScheduledInspection(
                id=inspection.id_inspeccion,
                claim_id=claim.id_siniestro,
                scheduled_at=inspection.fecha_programada,
                current_state=EstadoSiniestro(claim.estado_actual),
                version=claim.version,
            )

    def get(
        self,
        claim_id: int,
        inspection_id: int,
        principal: AuthenticatedPrincipal,
    ) -> ScheduledInspection | None:
        with self._factory() as session:
            if (
                PostgreSQLInspectionBudgetRepository._internal_identity_in_scope(
                    session,
                    claim_id,
                    principal,
                )
                is None
            ):
                return None
            inspection = session.get(Inspeccion, inspection_id)
            if inspection is None or inspection.id_siniestro != claim_id:
                return None
            claim = session.get(Siniestro, claim_id)
            if claim is None:
                return None
            return ScheduledInspection(
                id=inspection.id_inspeccion,
                claim_id=claim.id_siniestro,
                scheduled_at=inspection.fecha_programada,
                current_state=EstadoSiniestro(claim.estado_actual),
                version=claim.version,
            )
