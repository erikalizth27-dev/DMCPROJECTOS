from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import exists, select
from sqlalchemy.orm import Session, sessionmaker

from siniestro_facil.application.verify_coverage import (
    CoverageContext,
    CoverageVerification,
    CoverageVerificationError,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.enums import EstadoSiniestro
from siniestro_facil.domain.identity import AuthenticatedPrincipal
from siniestro_facil.persistence.models import (
    Asegurado,
    AsignacionSiniestro,
    Cobertura,
    EventoLineaTiempo,
    IdentidadActor,
    Poliza,
    Siniestro,
    UsuarioInterno,
    Vehiculo,
)


class PostgreSQLCoverageRepository:
    """Persiste cobertura, transición, versión y auditoría atómicamente."""

    def __init__(self, factory: sessionmaker[Session]) -> None:
        self._factory = factory

    @staticmethod
    def _identity_and_scope(
        session: Session,
        claim_id: int,
        principal: AuthenticatedPrincipal,
    ) -> tuple[IdentidadActor, UsuarioInterno] | None:
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
            return identity, user
        if principal.role not in {PrincipalRole.OPERADOR, PrincipalRole.AJUSTADOR}:
            return None
        in_scope = session.scalar(
            select(
                exists().where(
                    AsignacionSiniestro.id_usuario == identity.id_usuario,
                    AsignacionSiniestro.id_siniestro == claim_id,
                    AsignacionSiniestro.finalizado_en.is_(None),
                )
            )
        )
        return (identity, user) if in_scope else None

    def find_context(
        self,
        claim_id: int,
        principal: AuthenticatedPrincipal,
    ) -> CoverageContext | None:
        with self._factory() as session:
            if self._identity_and_scope(session, claim_id, principal) is None:
                return None
            row = session.execute(
                select(Siniestro, Poliza, Vehiculo, Asegurado)
                .join(Poliza, Poliza.id_poliza == Siniestro.id_poliza)
                .join(Vehiculo, Vehiculo.id_vehiculo == Siniestro.id_vehiculo)
                .join(Asegurado, Asegurado.id_asegurado == Poliza.id_asegurado)
                .where(Siniestro.id_siniestro == claim_id)
            ).one_or_none()
            if row is None:
                return None
            claim, policy, vehicle, insured = row
            return CoverageContext(
                claim_id=claim.id_siniestro,
                policy_number=policy.numero_poliza,
                document_number=insured.numero_documento,
                plate=vehicle.placa,
                event_date=claim.fecha_evento.date(),
                current_state=EstadoSiniestro(claim.estado_actual),
                version=claim.version,
            )

    def save_verification(
        self,
        context: CoverageContext,
        verification: CoverageVerification,
        principal: AuthenticatedPrincipal,
    ) -> CoverageVerification:
        with self._factory() as session, session.begin():
            identity_scope = self._identity_and_scope(
                session,
                context.claim_id,
                principal,
            )
            if identity_scope is None:
                raise CoverageVerificationError(
                    "CLAIM-NOT-FOUND",
                    "Siniestro no encontrado",
                    404,
                )
            identity, _ = identity_scope
            claim = session.execute(
                select(Siniestro)
                .where(Siniestro.id_siniestro == context.claim_id)
                .with_for_update()
            ).scalar_one_or_none()
            if claim is None:
                raise CoverageVerificationError(
                    "CLAIM-NOT-FOUND",
                    "Siniestro no encontrado",
                    404,
                )
            if claim.version != context.version:
                raise CoverageVerificationError(
                    "STATE-VERSION-CONFLICT",
                    "La versión del siniestro está desactualizada",
                    409,
                )
            if claim.estado_actual != EstadoSiniestro.REPORTADO.value:
                raise CoverageVerificationError(
                    "INVALID-COVERAGE-STATE",
                    "La cobertura sólo puede verificarse desde el estado reportado",
                    409,
                )

            coverage = session.execute(
                select(Cobertura)
                .where(Cobertura.id_poliza == claim.id_poliza)
                .order_by(Cobertura.id_cobertura)
                .limit(1)
                .with_for_update()
            ).scalar_one_or_none()
            if coverage is None:
                coverage = Cobertura(id_poliza=claim.id_poliza)
                session.add(coverage)
            coverage.deducible = verification.deductible
            coverage.estado_validacion = verification.validation_status

            previous_state = claim.estado_actual
            claim.estado_actual = verification.current_state.value
            claim.version = verification.version
            session.add(
                EventoLineaTiempo(
                    id_siniestro=claim.id_siniestro,
                    id_usuario=identity.id_usuario,
                    tipo_evento="cobertura_verificada",
                    fecha=datetime.now(timezone.utc),
                    detalle={
                        "estado_anterior": previous_state,
                        "estado_nuevo": verification.current_state.value,
                        "cobertura_activa": verification.active,
                        "deducible": str(verification.deductible),
                        "estado_validacion": verification.validation_status,
                        "requiere_revision_humana": verification.human_review_required,
                        "version_anterior": context.version,
                        "version_nueva": verification.version,
                        "adaptador": "simulado",
                    },
                )
            )
            session.flush()
            return verification
