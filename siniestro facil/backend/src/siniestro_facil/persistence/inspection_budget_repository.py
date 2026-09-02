from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from siniestro_facil.application.decide_budget import (
    BudgetDecisionError,
    DecideBudgetCommand,
    DecidedBudget,
)
from siniestro_facil.application.submit_budget import (
    BudgetSubmissionError,
    SubmitBudgetCommand,
    SubmittedBudget,
)
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
from siniestro_facil.domain.inspection_budget import (
    BudgetDecision,
    BudgetDecisionDenied,
    BudgetStatus,
    budget_is_expired,
    budget_valid_until,
    validate_budget_decision,
)
from siniestro_facil.domain.state_machine import (
    SolicitudTransicion,
    TransicionNoPermitida,
    validar_transicion,
)
from siniestro_facil.persistence.models import (
    AsignacionSiniestro,
    Autorizacion,
    CambioPresupuesto,
    EventoLineaTiempo,
    IdentidadActor,
    Inspeccion,
    Presupuesto,
    Siniestro,
    SolicitudDecisionPresupuestoIdempotente,
    SolicitudPresupuestoIdempotente,
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


class PostgreSQLBudgetSubmissionRepository:
    """Persiste presupuesto, transición, auditoría e idempotencia."""

    def __init__(self, factory: sessionmaker[Session]) -> None:
        self._factory = factory

    @staticmethod
    def _result_from_request(
        request: SolicitudPresupuestoIdempotente,
    ) -> SubmittedBudget:
        payload = request.respuesta
        return SubmittedBudget(
            id=int(payload["id"]),
            claim_id=int(payload["claim_id"]),
            inspection_id=int(payload["inspection_id"]),
            provider_id=int(payload["provider_id"]),
            diagnosis=str(payload["diagnosis"]),
            valid_from=datetime.fromisoformat(
                str(payload["valid_from"])
            ).date(),
            valid_until=datetime.fromisoformat(
                str(payload["valid_until"])
            ).date(),
            status=BudgetStatus(str(payload["status"])),
            current_state=EstadoSiniestro(str(payload["current_state"])),
            version=int(payload["version"]),
        )

    @staticmethod
    def _provider_identity(
        session: Session,
        principal: AuthenticatedPrincipal,
    ) -> IdentidadActor | None:
        identity = session.get(
            IdentidadActor,
            (principal.subject, principal.tenant_id),
        )
        if (
            identity is None
            or identity.actor_type != principal.actor_type.value
            or identity.id_proveedor is None
            or principal.role is not PrincipalRole.TALLER
        ):
            return None
        return identity

    def submit(
        self,
        command: SubmitBudgetCommand,
        principal: AuthenticatedPrincipal,
    ) -> SubmittedBudget:
        try:
            with self._factory() as session, session.begin():
                identity = self._provider_identity(session, principal)
                if identity is None:
                    raise BudgetSubmissionError(
                        "BUDGET-NOT-FOUND",
                        "Presupuesto no encontrado",
                        404,
                    )
                existing = session.get(
                    SolicitudPresupuestoIdempotente,
                    command.idempotency_key,
                )
                if existing is not None:
                    if existing.huella == command.fingerprint:
                        return self._result_from_request(existing)
                    raise BudgetSubmissionError(
                        "IDEMPOTENCY-CONFLICT",
                        "Idempotency-Key ya fue utilizada con otro contenido",
                        409,
                    )

                inspection = session.get(
                    Inspeccion,
                    command.inspection_id,
                    with_for_update=True,
                )
                if (
                    inspection is None
                    or inspection.id_siniestro != command.claim_id
                ):
                    raise BudgetSubmissionError(
                        "INSPECTION-NOT-FOUND",
                        "Inspección no encontrada",
                        404,
                    )
                claim = session.execute(
                    select(Siniestro)
                    .where(Siniestro.id_siniestro == command.claim_id)
                    .with_for_update()
                ).scalar_one_or_none()
                if claim is None:
                    raise BudgetSubmissionError(
                        "BUDGET-NOT-FOUND",
                        "Siniestro no encontrado",
                        404,
                    )
                if claim.version != command.expected_version:
                    raise BudgetSubmissionError(
                        "STATE-VERSION-CONFLICT",
                        "La versión del siniestro está desactualizada",
                        409,
                    )
                try:
                    validar_transicion(
                        SolicitudTransicion(
                            origen=EstadoSiniestro(claim.estado_actual),
                            destino=EstadoSiniestro.PRESUPUESTO_RECIBIDO,
                            rol=RolUsuario.OPERADOR,
                            motivo="Presupuesto presentado por taller",
                        )
                    )
                except (ValueError, TransicionNoPermitida) as exc:
                    raise BudgetSubmissionError(
                        "INVALID-TRANSITION",
                        str(exc),
                        409,
                    ) from exc

                now = datetime.now(timezone.utc)
                budget = Presupuesto(
                    id_siniestro=claim.id_siniestro,
                    id_inspeccion=inspection.id_inspeccion,
                    id_proveedor=identity.id_proveedor,
                    diagnostico=command.diagnosis.strip(),
                    vigencia_desde=command.presented_on,
                    vigencia_hasta=budget_valid_until(
                        command.presented_on
                    ),
                    estado=BudgetStatus.RECEIVED.value,
                )
                session.add(budget)
                previous_state = claim.estado_actual
                claim.estado_actual = EstadoSiniestro.PRESUPUESTO_RECIBIDO.value
                claim.version += 1
                session.flush()
                result = SubmittedBudget(
                    id=budget.id_presupuesto,
                    claim_id=claim.id_siniestro,
                    inspection_id=inspection.id_inspeccion,
                    provider_id=identity.id_proveedor,
                    diagnosis=budget.diagnostico or "",
                    valid_from=budget.vigencia_desde,
                    valid_until=budget.vigencia_hasta,
                    status=BudgetStatus(budget.estado),
                    current_state=EstadoSiniestro(claim.estado_actual),
                    version=claim.version,
                )
                session.add(
                    EventoLineaTiempo(
                        id_siniestro=claim.id_siniestro,
                        id_usuario=None,
                        tipo_evento="presupuesto_presentado",
                        fecha=now,
                        detalle={
                            "id_presupuesto": budget.id_presupuesto,
                            "id_inspeccion": inspection.id_inspeccion,
                            "id_proveedor": identity.id_proveedor,
                            "vigencia_desde": budget.vigencia_desde.isoformat(),
                            "vigencia_hasta": budget.vigencia_hasta.isoformat(),
                            "estado_anterior": previous_state,
                            "estado_nuevo": claim.estado_actual,
                            "version_anterior": command.expected_version,
                            "version_nueva": claim.version,
                            "actor_subject": principal.subject,
                        },
                    )
                )
                session.add(
                    SolicitudPresupuestoIdempotente(
                        clave=command.idempotency_key,
                        huella=command.fingerprint,
                        id_presupuesto=budget.id_presupuesto,
                        respuesta={
                            "id": result.id,
                            "claim_id": result.claim_id,
                            "inspection_id": result.inspection_id,
                            "provider_id": result.provider_id,
                            "diagnosis": result.diagnosis,
                            "valid_from": result.valid_from.isoformat(),
                            "valid_until": result.valid_until.isoformat(),
                            "status": result.status.value,
                            "current_state": result.current_state.value,
                            "version": result.version,
                        },
                        creado_en=now,
                    )
                )
                session.flush()
                return result
        except IntegrityError as exc:
            with self._factory() as session:
                existing = session.get(
                    SolicitudPresupuestoIdempotente,
                    command.idempotency_key,
                )
                if existing is not None:
                    if existing.huella == command.fingerprint:
                        return self._result_from_request(existing)
                    raise BudgetSubmissionError(
                        "IDEMPOTENCY-CONFLICT",
                        "Idempotency-Key ya fue utilizada con otro contenido",
                        409,
                    ) from exc
            raise BudgetSubmissionError(
                "BUDGET-CONFLICT",
                "El presupuesto no pudo registrarse",
                409,
            ) from exc

    def get(
        self,
        claim_id: int,
        budget_id: int,
        principal: AuthenticatedPrincipal,
    ) -> SubmittedBudget | None:
        with self._factory() as session:
            identity = self._provider_identity(session, principal)
            budget = session.get(Presupuesto, budget_id)
            if (
                identity is None
                or budget is None
                or budget.id_siniestro != claim_id
                or budget.id_proveedor != identity.id_proveedor
                or budget.id_inspeccion is None
            ):
                return None
            claim = session.get(Siniestro, claim_id)
            if claim is None:
                return None
            return SubmittedBudget(
                id=budget.id_presupuesto,
                claim_id=budget.id_siniestro,
                inspection_id=budget.id_inspeccion,
                provider_id=budget.id_proveedor,
                diagnosis=budget.diagnostico or "",
                valid_from=budget.vigencia_desde,
                valid_until=budget.vigencia_hasta,
                status=BudgetStatus(budget.estado),
                current_state=EstadoSiniestro(claim.estado_actual),
                version=claim.version,
            )


class PostgreSQLBudgetDecisionRepository:
    """Registra decisiones, cambios, auditoría e idempotencia atómicamente."""

    def __init__(self, factory: sessionmaker[Session]) -> None:
        self._factory = factory

    @staticmethod
    def _result_from_request(
        request: SolicitudDecisionPresupuestoIdempotente,
    ) -> DecidedBudget:
        payload = request.respuesta
        return DecidedBudget(
            decision_id=int(payload["decision_id"]),
            budget_id=int(payload["budget_id"]),
            claim_id=int(payload["claim_id"]),
            target=BudgetStatus(str(payload["target"])),
            reason=str(payload["reason"]),
            decided_at=datetime.fromisoformat(str(payload["decided_at"])),
            current_state=EstadoSiniestro(str(payload["current_state"])),
            version=int(payload["version"]),
        )

    def decide(
        self,
        command: DecideBudgetCommand,
        principal: AuthenticatedPrincipal,
    ) -> DecidedBudget:
        try:
            with self._factory() as session, session.begin():
                identity = PostgreSQLInspectionBudgetRepository._internal_identity_in_scope(
                    session,
                    command.claim_id,
                    principal,
                )
                if identity is None or identity.id_usuario is None:
                    raise BudgetDecisionError(
                        "BUDGET-NOT-FOUND",
                        "Presupuesto no encontrado",
                        404,
                    )
                existing = session.get(
                    SolicitudDecisionPresupuestoIdempotente,
                    command.idempotency_key,
                )
                if existing is not None:
                    if existing.huella == command.fingerprint:
                        return self._result_from_request(existing)
                    raise BudgetDecisionError(
                        "IDEMPOTENCY-CONFLICT",
                        "Idempotency-Key ya fue utilizada con otro contenido",
                        409,
                    )
                budget = session.get(
                    Presupuesto,
                    command.budget_id,
                    with_for_update=True,
                )
                if budget is None or budget.id_siniestro != command.claim_id:
                    raise BudgetDecisionError(
                        "BUDGET-NOT-FOUND",
                        "Presupuesto no encontrado",
                        404,
                    )
                claim = session.execute(
                    select(Siniestro)
                    .where(Siniestro.id_siniestro == command.claim_id)
                    .with_for_update()
                ).scalar_one_or_none()
                if claim is None:
                    raise BudgetDecisionError(
                        "BUDGET-NOT-FOUND",
                        "Presupuesto no encontrado",
                        404,
                    )
                if claim.version != command.expected_version:
                    raise BudgetDecisionError(
                        "STATE-VERSION-CONFLICT",
                        "La versión del siniestro está desactualizada",
                        409,
                    )
                if (
                    command.target is BudgetStatus.AUTHORIZED
                    and budget_is_expired(
                        valid_until=budget.vigencia_hasta,
                        evaluated_on=datetime.now(timezone.utc).date(),
                    )
                ):
                    raise BudgetDecisionError(
                        "BUDGET-EXPIRED",
                        "El presupuesto venció y requiere una nueva versión",
                        409,
                    )
                try:
                    validate_budget_decision(
                        BudgetDecision(
                            role=principal.role,
                            target=command.target,
                            actor_assigned=True,
                        )
                    )
                except BudgetDecisionDenied as exc:
                    raise BudgetDecisionError(
                        "BUDGET-DECISION-FORBIDDEN",
                        str(exc),
                        403,
                    ) from exc

                target_state = {
                    BudgetStatus.OBSERVED: EstadoSiniestro.OBSERVADO,
                    BudgetStatus.AUTHORIZED: EstadoSiniestro.AUTORIZADO,
                    BudgetStatus.REJECTED: EstadoSiniestro.RECHAZADO,
                }[command.target]
                now = datetime.now(timezone.utc)
                authorization = Autorizacion(
                    id_usuario_autoriza=identity.id_usuario,
                    fecha=now,
                    objeto_autorizado=(
                        f"presupuesto:{budget.id_presupuesto}:"
                        f"{command.target.value}"
                    ),
                )
                session.add(authorization)
                session.flush()
                change = CambioPresupuesto(
                    id_presupuesto=budget.id_presupuesto,
                    tipo_cambio=command.target.value,
                    id_autorizacion=authorization.id_autorizacion,
                )
                session.add(change)
                previous_state = claim.estado_actual
                previous_budget_status = budget.estado
                budget.estado = command.target.value
                claim.estado_actual = target_state.value
                claim.version += 1
                session.flush()
                result = DecidedBudget(
                    decision_id=change.id_cambio,
                    budget_id=budget.id_presupuesto,
                    claim_id=claim.id_siniestro,
                    target=command.target,
                    reason=command.reason.strip(),
                    decided_at=now,
                    current_state=target_state,
                    version=claim.version,
                )
                session.add(
                    EventoLineaTiempo(
                        id_siniestro=claim.id_siniestro,
                        id_usuario=identity.id_usuario,
                        tipo_evento="decision_presupuesto_registrada",
                        fecha=now,
                        detalle={
                            "id_presupuesto": budget.id_presupuesto,
                            "id_autorizacion": authorization.id_autorizacion,
                            "id_cambio": change.id_cambio,
                            "decision": command.target.value,
                            "justificacion": command.reason.strip(),
                            "estado_presupuesto_anterior": previous_budget_status,
                            "estado_siniestro_anterior": previous_state,
                            "estado_siniestro_nuevo": target_state.value,
                            "version_anterior": command.expected_version,
                            "version_nueva": claim.version,
                            "actor_subject": principal.subject,
                        },
                    )
                )
                session.add(
                    SolicitudDecisionPresupuestoIdempotente(
                        clave=command.idempotency_key,
                        huella=command.fingerprint,
                        id_cambio=change.id_cambio,
                        respuesta={
                            "decision_id": result.decision_id,
                            "budget_id": result.budget_id,
                            "claim_id": result.claim_id,
                            "target": result.target.value,
                            "reason": result.reason,
                            "decided_at": result.decided_at.isoformat(),
                            "current_state": result.current_state.value,
                            "version": result.version,
                        },
                        creado_en=now,
                    )
                )
                session.flush()
                return result
        except IntegrityError as exc:
            with self._factory() as session:
                existing = session.get(
                    SolicitudDecisionPresupuestoIdempotente,
                    command.idempotency_key,
                )
                if existing is not None:
                    if existing.huella == command.fingerprint:
                        return self._result_from_request(existing)
                    raise BudgetDecisionError(
                        "IDEMPOTENCY-CONFLICT",
                        "Idempotency-Key ya fue utilizada con otro contenido",
                        409,
                    ) from exc
            raise BudgetDecisionError(
                "BUDGET-DECISION-CONFLICT",
                "La decisión no pudo registrarse",
                409,
            ) from exc
