from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from siniestro_facil.application.register_evidence import (
    EvidenceRegistrationError,
    RegisterEvidenceCommand,
    RegisteredEvidence,
    StoredEvidenceRequest,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import AuthenticatedPrincipal
from siniestro_facil.persistence.models import (
    AsignacionSiniestro,
    Evidencia,
    EventoLineaTiempo,
    IdentidadActor,
    Poliza,
    Siniestro,
    SolicitudEvidenciaIdempotente,
    UsuarioInterno,
)


class PostgreSQLEvidenceRepository:
    """Persiste evidencia, auditoría e idempotencia en una transacción."""

    def __init__(self, factory: sessionmaker[Session]) -> None:
        self._factory = factory

    @staticmethod
    def _result_from_row(
        row: SolicitudEvidenciaIdempotente,
    ) -> RegisteredEvidence:
        payload = row.respuesta
        return RegisteredEvidence(
            id=int(payload["id"]),
            claim_id=int(payload["claim_id"]),
            evidence_type=str(payload["evidence_type"]),
            original_uri=str(payload["original_uri"]),
            sha256_hex=str(payload["sha256_hex"]),
            received_at=datetime.fromisoformat(
                str(payload["received_at"])
            ),
            derived_from_id=(
                int(payload["derived_from_id"])
                if payload.get("derived_from_id") is not None
                else None
            ),
        )

    @staticmethod
    def _identity_in_scope(
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
        ):
            return None

        if principal.role is PrincipalRole.ASEGURADO:
            if identity.id_asegurado is None:
                return None
            visible = session.scalar(
                select(
                    exists()
                    .select_from(Siniestro)
                    .join(
                        Poliza,
                        Poliza.id_poliza == Siniestro.id_poliza,
                    )
                    .where(
                        Siniestro.id_siniestro == claim_id,
                        Poliza.id_asegurado == identity.id_asegurado,
                    )
                )
            )
            return identity if visible else None

        if identity.id_usuario is None:
            return None
        user = session.get(UsuarioInterno, identity.id_usuario)
        if user is None or user.rol != principal.role.value:
            return None
        if principal.role is PrincipalRole.SUPERVISOR:
            return identity
        if principal.role in {
            PrincipalRole.OPERADOR,
            PrincipalRole.AJUSTADOR,
        }:
            assigned = session.scalar(
                select(
                    exists().where(
                        AsignacionSiniestro.id_usuario
                        == identity.id_usuario,
                        AsignacionSiniestro.id_siniestro == claim_id,
                        AsignacionSiniestro.finalizado_en.is_(None),
                    )
                )
            )
            return identity if assigned else None
        return None

    def find_request(
        self,
        idempotency_key: str,
        principal: AuthenticatedPrincipal,
    ) -> StoredEvidenceRequest | None:
        with self._factory() as session:
            row = session.get(
                SolicitudEvidenciaIdempotente,
                idempotency_key,
            )
            if row is None:
                return None
            evidence = session.get(Evidencia, row.id_evidencia)
            if (
                evidence is None
                or self._identity_in_scope(
                    session,
                    evidence.id_siniestro,
                    principal,
                )
                is None
            ):
                return None
            return StoredEvidenceRequest(
                row.huella,
                self._result_from_row(row),
            )

    def create(
        self,
        command: RegisterEvidenceCommand,
        principal: AuthenticatedPrincipal,
        *,
        idempotency_key: str,
        fingerprint: str,
    ) -> RegisteredEvidence:
        try:
            with self._factory() as session, session.begin():
                identity = self._identity_in_scope(
                    session,
                    command.claim_id,
                    principal,
                )
                if identity is None:
                    raise EvidenceRegistrationError(
                        "CLAIM-NOT-FOUND",
                        "Siniestro no encontrado",
                        404,
                    )
                existing = session.get(
                    SolicitudEvidenciaIdempotente,
                    idempotency_key,
                )
                if existing is not None:
                    if existing.huella == fingerprint:
                        return self._result_from_row(existing)
                    raise EvidenceRegistrationError(
                        "IDEMPOTENCY-CONFLICT",
                        "Idempotency-Key ya fue utilizada con otro contenido",
                        409,
                    )
                if command.derived_from_id is not None:
                    parent = session.get(
                        Evidencia,
                        command.derived_from_id,
                    )
                    if (
                        parent is None
                        or parent.id_siniestro != command.claim_id
                    ):
                        raise EvidenceRegistrationError(
                            "EVIDENCE-PARENT-NOT-FOUND",
                            "La evidencia original no está disponible",
                            422,
                        )

                now = datetime.now(timezone.utc)
                evidence = Evidencia(
                    id_siniestro=command.claim_id,
                    tipo_evidencia=command.evidence_type,
                    contenido_original_uri=command.original_uri,
                    hash=command.sha256_hex,
                    metadatos=command.metadata,
                    fecha_captura=command.captured_at,
                    fecha_recepcion=now,
                    fuente=command.source,
                    version_derivada_de=command.derived_from_id,
                )
                session.add(evidence)
                session.flush()

                result = RegisteredEvidence(
                    id=evidence.id_evidencia,
                    claim_id=evidence.id_siniestro,
                    evidence_type=evidence.tipo_evidencia,
                    original_uri=evidence.contenido_original_uri,
                    sha256_hex=evidence.hash,
                    received_at=evidence.fecha_recepcion,
                    derived_from_id=evidence.version_derivada_de,
                )
                session.add(
                    EventoLineaTiempo(
                        id_siniestro=command.claim_id,
                        id_usuario=identity.id_usuario,
                        tipo_evento="evidencia_registrada",
                        fecha=now,
                        detalle={
                            "id_evidencia": evidence.id_evidencia,
                            "tipo_evidencia": evidence.tipo_evidencia,
                            "hash": evidence.hash,
                            "uri": evidence.contenido_original_uri,
                            "version_derivada_de": (
                                evidence.version_derivada_de
                            ),
                            "actor_subject": principal.subject,
                        },
                    )
                )
                session.add(
                    SolicitudEvidenciaIdempotente(
                        clave=idempotency_key,
                        huella=fingerprint,
                        id_evidencia=evidence.id_evidencia,
                        respuesta={
                            "id": result.id,
                            "claim_id": result.claim_id,
                            "evidence_type": result.evidence_type,
                            "original_uri": result.original_uri,
                            "sha256_hex": result.sha256_hex,
                            "received_at": result.received_at.isoformat(),
                            "derived_from_id": result.derived_from_id,
                        },
                        creado_en=now,
                    )
                )
            return result
        except IntegrityError as exc:
            stored = self.find_request(
                idempotency_key,
                principal,
            )
            if stored is not None and stored.fingerprint == fingerprint:
                return stored.result
            if stored is not None:
                raise EvidenceRegistrationError(
                    "IDEMPOTENCY-CONFLICT",
                    "Idempotency-Key ya fue utilizada con otro contenido",
                    409,
                ) from exc
            raise EvidenceRegistrationError(
                "EVIDENCE-CONFLICT",
                "La evidencia ya fue registrada",
                409,
            ) from exc
