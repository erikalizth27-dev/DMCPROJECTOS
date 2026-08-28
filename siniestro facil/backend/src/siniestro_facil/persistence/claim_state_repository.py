from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import exists, select
from sqlalchemy.orm import Session, sessionmaker

from siniestro_facil.application.change_claim_state import (
    ChangeClaimStateCommand,
    ChangedClaimState,
    ClaimStateChangeError,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.enums import EstadoSiniestro, RolUsuario
from siniestro_facil.domain.identity import AuthenticatedPrincipal
from siniestro_facil.domain.state_machine import (
    SolicitudTransicion,
    TransicionNoPermitida,
    validar_transicion,
)
from siniestro_facil.persistence.models import (
    AsignacionSiniestro,
    EventoLineaTiempo,
    IdentidadActor,
    Siniestro,
    UsuarioInterno,
)


class PostgreSQLClaimStateRepository:
    """Cambia estado y registra auditoría dentro de una única transacción."""

    def __init__(self, factory: sessionmaker[Session]) -> None:
        self._factory = factory

    def change_state(
        self,
        command: ChangeClaimStateCommand,
        principal: AuthenticatedPrincipal,
    ) -> ChangedClaimState | None:
        with self._factory() as session, session.begin():
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
                in_scope = True
            elif principal.role in {PrincipalRole.OPERADOR, PrincipalRole.AJUSTADOR}:
                in_scope = session.scalar(
                    select(
                        exists().where(
                            AsignacionSiniestro.id_usuario == identity.id_usuario,
                            AsignacionSiniestro.id_siniestro == command.claim_id,
                            AsignacionSiniestro.finalizado_en.is_(None),
                        )
                    )
                )
            else:
                in_scope = False

            if not in_scope:
                return None

            claim = session.execute(
                select(Siniestro)
                .where(Siniestro.id_siniestro == command.claim_id)
                .with_for_update()
            ).scalar_one_or_none()
            if claim is None:
                return None

            if claim.version != command.expected_version:
                raise ClaimStateChangeError(
                    "STATE-VERSION-CONFLICT",
                    "La versión del siniestro está desactualizada",
                    409,
                )

            try:
                origin = EstadoSiniestro(claim.estado_actual)
                role = RolUsuario(principal.role.value)
                validar_transicion(
                    SolicitudTransicion(
                        origen=origin,
                        destino=command.target_state,
                        rol=role,
                        motivo=command.reason,
                        evidencia_completa=command.evidence_complete,
                        confirmacion_humana=command.human_confirmation,
                    )
                )
            except (ValueError, TransicionNoPermitida) as exc:
                raise ClaimStateChangeError(
                    "INVALID-TRANSITION",
                    str(exc),
                    409,
                ) from exc

            previous_state = claim.estado_actual
            claim.estado_actual = command.target_state.value
            claim.version += 1
            session.add(
                EventoLineaTiempo(
                    id_siniestro=claim.id_siniestro,
                    id_usuario=identity.id_usuario,
                    tipo_evento="cambio_estado",
                    fecha=datetime.now(timezone.utc),
                    detalle={
                        "estado_anterior": previous_state,
                        "estado_nuevo": command.target_state.value,
                        "motivo": command.reason.strip(),
                        "version_anterior": command.expected_version,
                        "version_nueva": claim.version,
                        "subject": principal.subject,
                        "tenant_id": principal.tenant_id,
                    },
                )
            )
            session.flush()
            return ChangedClaimState(
                id=claim.id_siniestro,
                current_state=command.target_state,
                version=claim.version,
            )
