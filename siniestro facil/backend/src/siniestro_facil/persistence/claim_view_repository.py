from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import exists, false, select
from sqlalchemy.orm import Session, sessionmaker

from siniestro_facil.application.get_claim_view import (
    ClaimView,
    NEXT_STEP_BY_STATE,
)
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


class PostgreSQLClaimViewRepository:
    def __init__(self, factory: sessionmaker[Session]) -> None:
        self._factory = factory

    def find_visible(
        self,
        claim_id: int,
        principal: AuthenticatedPrincipal,
    ) -> ClaimView | None:
        with self._factory() as session, session.begin():
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
                user = (
                    session.get(UsuarioInterno, identity.id_usuario)
                    if identity.id_usuario is not None
                    else None
                )
                if user is None or user.rol != principal.role.value:
                    return None

            if principal.role is PrincipalRole.SUPERVISOR:
                if identity.id_usuario is None:
                    return None
                scope = True
            elif principal.role is PrincipalRole.ASEGURADO:
                if identity.id_asegurado is None:
                    return None
                scope = Poliza.id_asegurado == identity.id_asegurado
            elif principal.role in {PrincipalRole.OPERADOR, PrincipalRole.AJUSTADOR}:
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
                # Taller e investigador requieren una orden/autorización
                # persistida; mientras no exista, denegación por defecto.
                scope = false()

            row = session.execute(
                select(Siniestro)
                .join(Poliza, Poliza.id_poliza == Siniestro.id_poliza)
                .where(Siniestro.id_siniestro == claim_id, scope)
            ).scalar_one_or_none()
            if row is None:
                return None

            if principal.role is PrincipalRole.SUPERVISOR:
                session.add(
                    EventoLineaTiempo(
                        id_siniestro=row.id_siniestro,
                        id_usuario=identity.id_usuario,
                        tipo_evento="consulta_sensible",
                        fecha=datetime.now(timezone.utc),
                        detalle={
                            "subject": principal.subject,
                            "tenant_id": principal.tenant_id,
                            "accion": "consultar_siniestro",
                            "resultado": "permitido",
                        },
                    )
                )

            return ClaimView(
                id=row.id_siniestro,
                estado_actual=row.estado_actual,
                fecha_evento=row.fecha_evento,
                tipo_evento=row.tipo_evento,
                siguiente_paso=NEXT_STEP_BY_STATE.get(row.estado_actual),
            )
