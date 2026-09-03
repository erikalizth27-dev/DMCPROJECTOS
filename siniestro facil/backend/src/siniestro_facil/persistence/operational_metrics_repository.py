from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from siniestro_facil.application.get_operational_metrics import (
    OperationalMetricFacts,
    OperationalMetricsError,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import AuthenticatedPrincipal
from siniestro_facil.persistence.models import (
    Asistencia,
    EventoLineaTiempo,
    IdentidadActor,
    Siniestro,
    UsuarioInterno,
)


TRACEABLE_DECISION_EVENTS = (
    "decision_presupuesto_registrada",
    "pago_autorizado",
)


class PostgreSQLOperationalMetricsRepository:
    def __init__(self, factory: sessionmaker[Session]) -> None:
        self._factory = factory

    @staticmethod
    def _validate_supervisor(
        session: Session,
        principal: AuthenticatedPrincipal,
    ) -> None:
        identity = session.get(
            IdentidadActor,
            (principal.subject, principal.tenant_id),
        )
        user = (
            session.get(UsuarioInterno, identity.id_usuario)
            if identity is not None and identity.id_usuario is not None
            else None
        )
        if (
            identity is None
            or identity.actor_type != principal.actor_type.value
            or principal.role is not PrincipalRole.SUPERVISOR
            or user is None
            or user.rol != PrincipalRole.SUPERVISOR.value
        ):
            raise OperationalMetricsError(
                "OPERATIONAL-METRICS-FORBIDDEN",
                "Solo el supervisor puede consultar indicadores",
                403,
            )

    def load_facts(
        self,
        *,
        period_start,
        period_end,
        principal: AuthenticatedPrincipal,
    ) -> OperationalMetricFacts:
        with self._factory() as session, session.begin():
            self._validate_supervisor(session, principal)
            claim = session.execute(
                select(Siniestro)
                .where(
                    Siniestro.creado_en >= period_start,
                    Siniestro.creado_en <= period_end,
                )
                .order_by(
                    Siniestro.creado_en,
                    Siniestro.id_siniestro,
                )
                .limit(1)
            ).scalar_one_or_none()
            if claim is None:
                return OperationalMetricFacts(None, None, None, None)

            first_assistance = session.scalar(
                select(func.min(Asistencia.creado_en)).where(
                    Asistencia.id_siniestro == claim.id_siniestro,
                    Asistencia.creado_en >= claim.creado_en,
                    Asistencia.creado_en <= period_end,
                )
            )
            first_decision = session.scalar(
                select(func.min(EventoLineaTiempo.fecha)).where(
                    EventoLineaTiempo.id_siniestro == claim.id_siniestro,
                    EventoLineaTiempo.tipo_evento.in_(
                        TRACEABLE_DECISION_EVENTS
                    ),
                    EventoLineaTiempo.fecha >= claim.creado_en,
                    EventoLineaTiempo.fecha <= period_end,
                )
            )
            return OperationalMetricFacts(
                claim_created_at=claim.creado_en,
                first_assistance_at=first_assistance,
                first_decision_at=first_decision,
                source_claim_id=claim.id_siniestro,
            )
