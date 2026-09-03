from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import exists, false, select
from sqlalchemy.orm import Session, sessionmaker

from siniestro_facil.application.get_claim_timeline import TimelineSlice
from siniestro_facil.domain.audit import TimelineEvent
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import AuthenticatedPrincipal
from siniestro_facil.persistence.models import (
    AsignacionSiniestro,
    EventoLineaTiempo,
    IdentidadActor,
    Poliza,
    Siniestro,
    UsuarioInterno,
)


SENSITIVE_EVENT_PREFIXES = (
    "alerta_",
    "evaluacion_fraude",
    "relacion_casos",
    "consulta_sensible",
    "consulta_auditoria_sensible",
)


class PostgreSQLClaimTimelineRepository:
    def __init__(self, factory: sessionmaker[Session]) -> None:
        self._factory = factory

    @staticmethod
    def _identity(
        session: Session,
        principal: AuthenticatedPrincipal,
    ) -> IdentidadActor | None:
        identity = session.get(
            IdentidadActor,
            (principal.subject, principal.tenant_id),
        )
        if identity is None or identity.actor_type != principal.actor_type.value:
            return None
        if principal.role in {
            PrincipalRole.OPERADOR,
            PrincipalRole.AJUSTADOR,
            PrincipalRole.INVESTIGADOR_FRAUDE,
            PrincipalRole.SUPERVISOR,
        }:
            if identity.id_usuario is None:
                return None
            user = session.get(UsuarioInterno, identity.id_usuario)
            if user is None or user.rol != principal.role.value:
                return None
        return identity

    @staticmethod
    def _visible_claim(
        session: Session,
        claim_id: int,
        principal: AuthenticatedPrincipal,
        identity: IdentidadActor,
    ) -> Siniestro | None:
        if principal.role is PrincipalRole.SUPERVISOR:
            if identity.id_usuario is None:
                return None
            scope = True
        elif principal.role is PrincipalRole.ASEGURADO:
            if identity.id_asegurado is None:
                return None
            scope = Poliza.id_asegurado == identity.id_asegurado
        elif principal.role in {
            PrincipalRole.OPERADOR,
            PrincipalRole.AJUSTADOR,
            PrincipalRole.INVESTIGADOR_FRAUDE,
        }:
            if identity.id_usuario is None:
                return None
            scope = exists(
                select(1)
                .select_from(AsignacionSiniestro)
                .where(
                    AsignacionSiniestro.id_usuario == identity.id_usuario,
                    AsignacionSiniestro.id_siniestro
                    == Siniestro.id_siniestro,
                    AsignacionSiniestro.finalizado_en.is_(None),
                )
            )
        else:
            scope = false()

        return session.execute(
            select(Siniestro)
            .join(Poliza, Poliza.id_poliza == Siniestro.id_poliza)
            .where(Siniestro.id_siniestro == claim_id, scope)
        ).scalar_one_or_none()

    @staticmethod
    def _sensitive(event_type: str) -> bool:
        return event_type.startswith(SENSITIVE_EVENT_PREFIXES)

    def list_visible(
        self,
        claim_id: int,
        principal: AuthenticatedPrincipal,
        *,
        after_event_id: int,
        page_size: int | None,
    ) -> TimelineSlice | None:
        with self._factory() as session, session.begin():
            identity = self._identity(session, principal)
            if identity is None:
                return None
            claim = self._visible_claim(
                session, claim_id, principal, identity
            )
            if claim is None:
                return None

            statement = (
                select(EventoLineaTiempo)
                .where(
                    EventoLineaTiempo.id_siniestro == claim.id_siniestro,
                    EventoLineaTiempo.id_evento > after_event_id,
                )
                .order_by(EventoLineaTiempo.id_evento)
            )
            if page_size is not None:
                statement = statement.limit(page_size + 1)
            rows = list(session.scalars(statement))
            has_more = page_size is not None and len(rows) > page_size
            if has_more:
                rows = rows[:page_size]
            events = tuple(
                TimelineEvent(
                    event_id=row.id_evento,
                    claim_id=row.id_siniestro,
                    event_type=row.tipo_evento,
                    actor_id=row.id_usuario,
                    detail=dict(row.detalle or {}),
                    sensitive=self._sensitive(row.tipo_evento),
                    occurred_at=row.fecha,
                )
                for row in rows
            )
            next_cursor = (
                events[-1].event_id if has_more and events else None
            )
            return TimelineSlice(events, next_cursor)

    def record_sensitive_access(
        self,
        claim_id: int,
        principal: AuthenticatedPrincipal,
        *,
        event_ids: tuple[int, ...],
    ) -> None:
        with self._factory() as session, session.begin():
            identity = self._identity(session, principal)
            if identity is None or identity.id_usuario is None:
                return
            claim = self._visible_claim(
                session, claim_id, principal, identity
            )
            if claim is None:
                return
            session.add(
                EventoLineaTiempo(
                    id_siniestro=claim.id_siniestro,
                    id_usuario=identity.id_usuario,
                    tipo_evento="consulta_auditoria_sensible",
                    fecha=datetime.now(timezone.utc),
                    detalle={
                        "subject": principal.subject,
                        "tenant_id": principal.tenant_id,
                        "eventos_consultados": list(event_ids),
                        "resultado": "permitido",
                    },
                )
            )
