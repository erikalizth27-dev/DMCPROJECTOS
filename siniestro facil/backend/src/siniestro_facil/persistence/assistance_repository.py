from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from siniestro_facil.application.assistance_contracts import AssistanceRecord
from siniestro_facil.application.manage_assistance import (
    MAX_PILOT_ATTEMPTS,
    AssistanceManagementError,
    ReassignAssistanceCommand,
    RegisterProviderReplyCommand,
)
from siniestro_facil.application.request_assistance import (
    AssistanceRequestError,
    RequestAssistanceCommand,
    StoredAssistanceRequest,
)
from siniestro_facil.domain.assistance import (
    AssistanceStatus,
    InvalidAssistanceTransition,
    ProviderResult,
    validate_assistance_transition,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import AuthenticatedPrincipal
from siniestro_facil.persistence.models import (
    AsignacionSiniestro,
    Asistencia,
    EventoLineaTiempo,
    IdentidadActor,
    Poliza,
    Proveedor,
    Siniestro,
    SolicitudAsistenciaIdempotente,
    UsuarioInterno,
)


class PostgreSQLAssistanceRepository:
    """Persiste asistencia, auditoría e idempotencia de S3-BE-01."""

    def __init__(self, factory: sessionmaker[Session]) -> None:
        self._factory = factory

    @staticmethod
    def _record(row: Asistencia) -> AssistanceRecord:
        return AssistanceRecord(
            id=row.id_asistencia,
            claim_id=row.id_siniestro,
            provider_id=row.id_proveedor,
            assistance_type=row.tipo_asistencia,
            status=AssistanceStatus(row.estado_solicitud),
            attempt=row.numero_intento,
            created_at=row.creado_en,
            updated_at=row.actualizado_en,
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
                    .join(Poliza, Poliza.id_poliza == Siniestro.id_poliza)
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
        assigned = session.scalar(
            select(
                exists().where(
                    AsignacionSiniestro.id_usuario == identity.id_usuario,
                    AsignacionSiniestro.id_siniestro == claim_id,
                    AsignacionSiniestro.finalizado_en.is_(None),
                )
            )
        )
        return identity if assigned else None

    @staticmethod
    def _stored(
        row: SolicitudAsistenciaIdempotente,
        assistance: Asistencia,
    ) -> StoredAssistanceRequest:
        return StoredAssistanceRequest(
            fingerprint=row.huella,
            result=PostgreSQLAssistanceRepository._record(assistance),
        )

    def find_request(
        self,
        idempotency_key: str,
        principal: AuthenticatedPrincipal,
    ) -> StoredAssistanceRequest | None:
        with self._factory() as session:
            row = session.get(
                SolicitudAsistenciaIdempotente,
                idempotency_key,
            )
            if row is None:
                return None
            assistance = session.get(Asistencia, row.id_asistencia)
            if (
                assistance is None
                or self._identity_in_scope(
                    session,
                    assistance.id_siniestro,
                    principal,
                )
                is None
            ):
                return None
            return self._stored(row, assistance)

    def create(
        self,
        command: RequestAssistanceCommand,
        principal: AuthenticatedPrincipal,
        *,
        idempotency_key: str,
        fingerprint: str,
    ) -> AssistanceRecord:
        try:
            with self._factory() as session, session.begin():
                identity = self._identity_in_scope(
                    session,
                    command.claim_id,
                    principal,
                )
                if identity is None:
                    raise AssistanceRequestError(
                        "CLAIM-NOT-FOUND",
                        "Siniestro no encontrado",
                        404,
                    )
                provider = session.get(Proveedor, command.provider_id)
                if provider is None:
                    raise AssistanceRequestError(
                        "PROVIDER-NOT-FOUND",
                        "Proveedor no encontrado",
                        404,
                    )
                existing = session.get(
                    SolicitudAsistenciaIdempotente,
                    idempotency_key,
                )
                if existing is not None:
                    assistance = session.get(
                        Asistencia,
                        existing.id_asistencia,
                    )
                    if (
                        assistance is not None
                        and existing.huella == fingerprint
                    ):
                        return self._record(assistance)
                    raise AssistanceRequestError(
                        "IDEMPOTENCY-CONFLICT",
                        "Idempotency-Key ya fue utilizada con otro contenido",
                        409,
                    )

                now = datetime.now(timezone.utc)
                assistance = Asistencia(
                    id_siniestro=command.claim_id,
                    id_proveedor=command.provider_id,
                    estado_solicitud=AssistanceStatus.PENDING.value,
                    numero_intento=1,
                    tipo_asistencia=command.assistance_type,
                    motivo=command.reason,
                    creado_en=now,
                    actualizado_en=now,
                )
                session.add(assistance)
                session.flush()
                result = self._record(assistance)
                session.add(
                    EventoLineaTiempo(
                        id_siniestro=command.claim_id,
                        id_usuario=identity.id_usuario,
                        tipo_evento="asistencia_solicitada",
                        fecha=now,
                        detalle={
                            "id_asistencia": assistance.id_asistencia,
                            "id_proveedor": assistance.id_proveedor,
                            "tipo_asistencia": assistance.tipo_asistencia,
                            "numero_intento": assistance.numero_intento,
                            "actor_subject": principal.subject,
                        },
                    )
                )
                session.add(
                    SolicitudAsistenciaIdempotente(
                        clave=idempotency_key,
                        huella=fingerprint,
                        id_asistencia=assistance.id_asistencia,
                        respuesta={
                            "id": result.id,
                            "claim_id": result.claim_id,
                            "provider_id": result.provider_id,
                            "status": result.status.value,
                        },
                        creado_en=now,
                    )
                )
            return result
        except IntegrityError as exc:
            stored = self.find_request(idempotency_key, principal)
            if stored is not None and stored.fingerprint == fingerprint:
                return stored.result
            raise AssistanceRequestError(
                "ASSISTANCE-CONFLICT",
                "La solicitud de asistencia ya fue registrada",
                409,
            ) from exc

    def mark_sent(
        self,
        assistance_id: int,
        external_reference: str,
        principal: AuthenticatedPrincipal,
    ) -> AssistanceRecord:
        with self._factory() as session, session.begin():
            assistance = session.get(
                Asistencia,
                assistance_id,
                with_for_update=True,
            )
            if (
                assistance is None
                or self._identity_in_scope(
                    session,
                    assistance.id_siniestro,
                    principal,
                )
                is None
            ):
                raise AssistanceRequestError(
                    "ASSISTANCE-NOT-FOUND",
                    "Asistencia no encontrada",
                    404,
                )
            if assistance.estado_solicitud == AssistanceStatus.SENT.value:
                return self._record(assistance)
            now = datetime.now(timezone.utc)
            assistance.estado_solicitud = AssistanceStatus.SENT.value
            assistance.referencia_externa = external_reference
            assistance.actualizado_en = now
            request = session.scalar(
                select(SolicitudAsistenciaIdempotente).where(
                    SolicitudAsistenciaIdempotente.id_asistencia
                    == assistance_id
                )
            )
            if request is None:
                raise AssistanceRequestError(
                    "ASSISTANCE-IDEMPOTENCY-MISSING",
                    "No existe control idempotente para la asistencia",
                    500,
                )
            result = self._record(assistance)
            request.respuesta = {
                "id": result.id,
                "claim_id": result.claim_id,
                "provider_id": result.provider_id,
                "status": result.status.value,
                "external_reference": external_reference,
            }
            session.add(
                EventoLineaTiempo(
                    id_siniestro=assistance.id_siniestro,
                    id_usuario=self._identity_in_scope(
                        session,
                        assistance.id_siniestro,
                        principal,
                    ).id_usuario,
                    tipo_evento="asistencia_enviada",
                    fecha=now,
                    detalle={
                        "id_asistencia": assistance.id_asistencia,
                        "id_proveedor": assistance.id_proveedor,
                        "referencia_externa": external_reference,
                        "numero_intento": assistance.numero_intento,
                        "actor_subject": principal.subject,
                    },
                )
            )
        return result

    def get(
        self,
        claim_id: int,
        assistance_id: int,
        principal: AuthenticatedPrincipal,
    ) -> AssistanceRecord | None:
        with self._factory() as session:
            if self._identity_in_scope(
                session,
                claim_id,
                principal,
            ) is None:
                return None
            assistance = session.get(Asistencia, assistance_id)
            if (
                assistance is None
                or assistance.id_siniestro != claim_id
            ):
                return None
            return self._record(assistance)


    @staticmethod
    def _check_expected_attempt(
        assistance: Asistencia,
        expected_attempt: int,
    ) -> None:
        if assistance.numero_intento != expected_attempt:
            raise AssistanceManagementError(
                "ASSISTANCE-VERSION-CONFLICT",
                "La asistencia fue modificada por otra operación",
                409,
            )

    def register_reply(
        self,
        command: RegisterProviderReplyCommand,
        principal: AuthenticatedPrincipal,
    ) -> AssistanceRecord:
        with self._factory() as session, session.begin():
            assistance = session.get(
                Asistencia,
                command.assistance_id,
                with_for_update=True,
            )
            identity = (
                self._identity_in_scope(
                    session,
                    command.claim_id,
                    principal,
                )
                if assistance is not None
                else None
            )
            if (
                assistance is None
                or assistance.id_siniestro != command.claim_id
                or identity is None
            ):
                raise AssistanceManagementError(
                    "ASSISTANCE-NOT-FOUND",
                    "Asistencia no encontrada",
                    404,
                )
            self._check_expected_attempt(
                assistance,
                command.expected_attempt,
            )
            target = {
                ProviderResult.ACCEPTED: AssistanceStatus.ACCEPTED,
                ProviderResult.REJECTED: AssistanceStatus.REJECTED,
                ProviderResult.NO_RESPONSE: AssistanceStatus.NO_RESPONSE,
            }[command.result]
            try:
                validate_assistance_transition(
                    AssistanceStatus(assistance.estado_solicitud),
                    target,
                )
            except InvalidAssistanceTransition as exc:
                raise AssistanceManagementError(
                    "ASSISTANCE-TRANSITION-INVALID",
                    str(exc),
                    409,
                ) from exc

            now = datetime.now(timezone.utc)
            assistance.estado_solicitud = target.value
            assistance.actualizado_en = now
            if command.external_reference:
                assistance.referencia_externa = (
                    command.external_reference.strip()
                )
            session.add(
                EventoLineaTiempo(
                    id_siniestro=assistance.id_siniestro,
                    id_usuario=identity.id_usuario,
                    tipo_evento="respuesta_proveedor_registrada",
                    fecha=now,
                    detalle={
                        "id_asistencia": assistance.id_asistencia,
                        "id_proveedor": assistance.id_proveedor,
                        "resultado": target.value,
                        "numero_intento": assistance.numero_intento,
                        "referencia_externa": (
                            assistance.referencia_externa
                        ),
                        "actor_subject": principal.subject,
                    },
                )
            )
            result = self._record(assistance)
        return result

    def reassign(
        self,
        command: ReassignAssistanceCommand,
        principal: AuthenticatedPrincipal,
    ) -> AssistanceRecord:
        try:
            with self._factory() as session, session.begin():
                current = session.get(
                    Asistencia,
                    command.assistance_id,
                    with_for_update=True,
                )
                identity = (
                    self._identity_in_scope(
                        session,
                        command.claim_id,
                        principal,
                    )
                    if current is not None
                    else None
                )
                if (
                    current is None
                    or current.id_siniestro != command.claim_id
                    or identity is None
                ):
                    raise AssistanceManagementError(
                        "ASSISTANCE-NOT-FOUND",
                        "Asistencia no encontrada",
                        404,
                    )
                self._check_expected_attempt(
                    current,
                    command.expected_attempt,
                )
                if current.estado_solicitud not in {
                    AssistanceStatus.REJECTED.value,
                    AssistanceStatus.NO_RESPONSE.value,
                }:
                    raise AssistanceManagementError(
                        "ASSISTANCE-REASSIGNMENT-INVALID",
                        (
                            "Solo se reasigna una solicitud rechazada "
                            "o sin respuesta"
                        ),
                        409,
                    )
                if current.numero_intento >= MAX_PILOT_ATTEMPTS:
                    raise AssistanceManagementError(
                        "RETRY-LIMIT-REACHED",
                        "Se alcanzó el máximo de intentos del piloto",
                        409,
                    )
                if (
                    command.new_provider_id <= 0
                    or command.new_provider_id == current.id_proveedor
                ):
                    raise AssistanceManagementError(
                        "PROVIDER-INVALID",
                        (
                            "El nuevo proveedor debe ser válido "
                            "y diferente"
                        ),
                        422,
                    )
                reason = command.reason.strip()
                if not reason:
                    raise AssistanceManagementError(
                        "REASSIGNMENT-REASON-REQUIRED",
                        "El motivo de reasignación es obligatorio",
                        422,
                    )
                provider = session.get(
                    Proveedor,
                    command.new_provider_id,
                )
                if provider is None:
                    raise AssistanceManagementError(
                        "PROVIDER-NOT-FOUND",
                        "Proveedor no encontrado",
                        404,
                    )

                now = datetime.now(timezone.utc)
                replacement = Asistencia(
                    id_siniestro=current.id_siniestro,
                    id_proveedor=command.new_provider_id,
                    estado_solicitud=AssistanceStatus.PENDING.value,
                    numero_intento=current.numero_intento + 1,
                    tipo_asistencia=current.tipo_asistencia,
                    motivo=reason,
                    creado_en=now,
                    actualizado_en=now,
                )
                session.add(replacement)
                session.flush()
                session.add(
                    EventoLineaTiempo(
                        id_siniestro=current.id_siniestro,
                        id_usuario=identity.id_usuario,
                        tipo_evento="asistencia_reasignada",
                        fecha=now,
                        detalle={
                            "id_asistencia_anterior": (
                                current.id_asistencia
                            ),
                            "id_proveedor_anterior": (
                                current.id_proveedor
                            ),
                            "id_asistencia_nueva": (
                                replacement.id_asistencia
                            ),
                            "id_proveedor_nuevo": (
                                replacement.id_proveedor
                            ),
                            "numero_intento": (
                                replacement.numero_intento
                            ),
                            "motivo": reason,
                            "actor_subject": principal.subject,
                        },
                    )
                )
                result = self._record(replacement)
            return result
        except IntegrityError as exc:
            raise AssistanceManagementError(
                "ASSISTANCE-REASSIGNMENT-CONFLICT",
                "La reasignación ya fue registrada",
                409,
            ) from exc
