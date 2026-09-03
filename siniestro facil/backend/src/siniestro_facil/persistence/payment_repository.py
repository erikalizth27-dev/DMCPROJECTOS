from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from siniestro_facil.application.manage_payment import (
    InMemoryPaymentRepository,
    PaymentOperationError,
    PaymentRecord,
    StoredPaymentRequest,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import AuthenticatedPrincipal
from siniestro_facil.domain.payment import PaymentStatus
from siniestro_facil.persistence.models import (
    Alerta,
    AsignacionSiniestro,
    Autorizacion,
    EventoLineaTiempo,
    IdentidadActor,
    Pago,
    Siniestro,
    SolicitudAutorizacionPagoIdempotente,
    SolicitudPreparacionPagoIdempotente,
    UsuarioInterno,
)


class PostgreSQLPaymentRepository(InMemoryPaymentRepository):
    """Persiste preparación, autorización, auditoría e idempotencia."""

    def __init__(self, factory: sessionmaker[Session]) -> None:
        self._factory = factory

    @staticmethod
    def _serialize(result: PaymentRecord) -> dict[str, object]:
        return {
            "id": result.id,
            "claim_id": result.claim_id,
            "amount": str(result.amount),
            "status": result.status.value,
            "preparer_subject": result.preparer_subject,
            "authorizer_subject": result.authorizer_subject,
            "version": result.version,
            "simulated": result.simulated,
            "money_transferred": result.money_transferred,
        }

    @staticmethod
    def _deserialize(payload: dict[str, object]) -> PaymentRecord:
        authorizer = payload.get("authorizer_subject")
        return PaymentRecord(
            id=int(payload["id"]),
            claim_id=int(payload["claim_id"]),
            amount=Decimal(str(payload["amount"])),
            status=PaymentStatus(str(payload["status"])),
            preparer_subject=str(payload["preparer_subject"]),
            authorizer_subject=(
                str(authorizer) if authorizer is not None else None
            ),
            version=int(payload["version"]),
            simulated=bool(payload.get("simulated", True)),
            money_transferred=bool(
                payload.get("money_transferred", False)
            ),
        )

    @staticmethod
    def _identity(
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
            or identity.id_usuario is None
        ):
            return None
        user = session.get(UsuarioInterno, identity.id_usuario)
        if user is None or user.rol != principal.role.value:
            return None
        return identity

    @staticmethod
    def _can_prepare(
        session: Session,
        claim_id: int,
        principal: AuthenticatedPrincipal,
        identity: IdentidadActor,
    ) -> bool:
        if principal.role is PrincipalRole.SUPERVISOR:
            return True
        if principal.role not in {
            PrincipalRole.OPERADOR,
            PrincipalRole.AJUSTADOR,
        }:
            return False
        return bool(
            session.scalar(
                select(
                    exists().where(
                        AsignacionSiniestro.id_siniestro == claim_id,
                        AsignacionSiniestro.id_usuario
                        == identity.id_usuario,
                        AsignacionSiniestro.finalizado_en.is_(None),
                    )
                )
            )
        )

    @staticmethod
    def _subject_for_user(
        session: Session,
        user_id: int | None,
    ) -> str | None:
        if user_id is None:
            return None
        return session.scalar(
            select(IdentidadActor.subject)
            .where(IdentidadActor.id_usuario == user_id)
            .limit(1)
        )

    @classmethod
    def _record(cls, session: Session, row: Pago) -> PaymentRecord:
        authorizer_user: int | None = None
        if row.id_autorizacion is not None:
            authorization = session.get(
                Autorizacion,
                row.id_autorizacion,
            )
            if authorization is not None:
                authorizer_user = authorization.id_usuario_autoriza
        preparer_subject = cls._subject_for_user(
            session,
            row.id_usuario_prepara,
        )
        return PaymentRecord(
            id=row.id_pago,
            claim_id=row.id_siniestro,
            amount=row.monto,
            status=PaymentStatus(row.estado),
            preparer_subject=preparer_subject or "",
            authorizer_subject=cls._subject_for_user(
                session,
                authorizer_user,
            ),
            version=row.version,
            simulated=True,
            money_transferred=False,
        )

    def find_prepare_request(
        self,
        idempotency_key: str,
    ) -> StoredPaymentRequest | None:
        with self._factory() as session:
            row = session.get(
                SolicitudPreparacionPagoIdempotente,
                idempotency_key,
            )
            if row is None:
                return None
            return StoredPaymentRequest(
                row.huella,
                self._deserialize(row.respuesta),
            )

    def prepare(
        self,
        request,
        principal: AuthenticatedPrincipal,
        *,
        idempotency_key: str,
        fingerprint: str,
    ) -> PaymentRecord:
        try:
            with self._factory() as session, session.begin():
                existing = session.get(
                    SolicitudPreparacionPagoIdempotente,
                    idempotency_key,
                    with_for_update=True,
                )
                if existing is not None:
                    if existing.huella == fingerprint:
                        return self._deserialize(existing.respuesta)
                    raise PaymentOperationError(
                        "IDEMPOTENCY-CONFLICT",
                        "Idempotency-Key ya fue utilizada con otro contenido",
                        409,
                    )
                identity = self._identity(session, principal)
                if (
                    identity is None
                    or identity.id_usuario is None
                    or not self._can_prepare(
                        session,
                        request.claim_id,
                        principal,
                        identity,
                    )
                ):
                    raise PaymentOperationError(
                        "PAYMENT-NOT-FOUND",
                        "Siniestro no encontrado",
                        404,
                    )
                claim = session.get(
                    Siniestro,
                    request.claim_id,
                    with_for_update=True,
                )
                if claim is None:
                    raise PaymentOperationError(
                        "PAYMENT-NOT-FOUND",
                        "Siniestro no encontrado",
                        404,
                    )
                now = datetime.now(timezone.utc)
                row = Pago(
                    id_siniestro=claim.id_siniestro,
                    id_autorizacion=None,
                    id_usuario_prepara=identity.id_usuario,
                    monto=request.amount,
                    estado=PaymentStatus.BLOQUEADO.value,
                    version=0,
                )
                session.add(row)
                session.flush()
                result = PaymentRecord(
                    id=row.id_pago,
                    claim_id=row.id_siniestro,
                    amount=row.monto,
                    status=PaymentStatus(row.estado),
                    preparer_subject=principal.subject,
                    authorizer_subject=None,
                    version=row.version,
                )
                session.add(
                    EventoLineaTiempo(
                        id_siniestro=claim.id_siniestro,
                        id_usuario=identity.id_usuario,
                        tipo_evento="pago_preparado",
                        fecha=now,
                        detalle={
                            "id_pago": row.id_pago,
                            "monto": str(row.monto),
                            "estado": row.estado,
                            "simulado": True,
                            "transferencia_realizada": False,
                        },
                    )
                )
                session.add(
                    SolicitudPreparacionPagoIdempotente(
                        clave=idempotency_key,
                        huella=fingerprint,
                        id_pago=row.id_pago,
                        respuesta=self._serialize(result),
                        creado_en=now,
                    )
                )
            return result
        except IntegrityError as exc:
            stored = self.find_prepare_request(idempotency_key)
            if stored is not None and stored.fingerprint == fingerprint:
                return stored.result
            if stored is not None:
                raise PaymentOperationError(
                    "IDEMPOTENCY-CONFLICT",
                    "Idempotency-Key ya fue utilizada con otro contenido",
                    409,
                ) from exc
            raise

    def find_authorize_request(
        self,
        idempotency_key: str,
    ) -> StoredPaymentRequest | None:
        with self._factory() as session:
            row = session.get(
                SolicitudAutorizacionPagoIdempotente,
                idempotency_key,
            )
            if row is None:
                return None
            return StoredPaymentRequest(
                row.huella,
                self._deserialize(row.respuesta),
            )

    def get(
        self,
        claim_id: int,
        payment_id: int,
    ) -> PaymentRecord | None:
        with self._factory() as session:
            row = session.get(Pago, payment_id)
            if row is None or row.id_siniestro != claim_id:
                return None
            return self._record(session, row)

    def has_pending_critical_alert(self, claim_id: int) -> bool:
        with self._factory() as session:
            return bool(
                session.scalar(
                    select(
                        exists().where(
                            Alerta.id_siniestro == claim_id,
                            Alerta.severidad == "critica",
                            Alerta.estado_revision == "pendiente",
                        )
                    )
                )
            )

    def authorize(
        self,
        payment: PaymentRecord,
        principal: AuthenticatedPrincipal,
        *,
        idempotency_key: str,
        fingerprint: str,
    ) -> PaymentRecord:
        try:
            with self._factory() as session, session.begin():
                existing = session.get(
                    SolicitudAutorizacionPagoIdempotente,
                    idempotency_key,
                    with_for_update=True,
                )
                if existing is not None:
                    if existing.huella == fingerprint:
                        return self._deserialize(existing.respuesta)
                    raise PaymentOperationError(
                        "IDEMPOTENCY-CONFLICT",
                        "Idempotency-Key ya fue utilizada con otro contenido",
                        409,
                    )
                identity = self._identity(session, principal)
                if (
                    identity is None
                    or identity.id_usuario is None
                    or principal.role is not PrincipalRole.SUPERVISOR
                ):
                    raise PaymentOperationError(
                        "PAYMENT-AUTHORIZE-FORBIDDEN",
                        "Solo un supervisor puede autorizar pagos",
                        403,
                    )
                row = session.execute(
                    select(Pago)
                    .where(
                        Pago.id_pago == payment.id,
                        Pago.id_siniestro == payment.claim_id,
                    )
                    .with_for_update()
                ).scalar_one_or_none()
                if row is None:
                    raise PaymentOperationError(
                        "PAYMENT-NOT-FOUND",
                        "Pago no encontrado",
                        404,
                    )
                if row.version != payment.version:
                    raise PaymentOperationError(
                        "PAYMENT-VERSION-CONFLICT",
                        "El pago fue modificado por otra operación",
                        409,
                    )
                if row.estado == PaymentStatus.EMITIDO.value:
                    raise PaymentOperationError(
                        "PAYMENT-ALREADY-AUTHORIZED",
                        "El pago ya fue autorizado",
                        409,
                    )
                if row.id_usuario_prepara is None:
                    raise PaymentOperationError(
                        "PAYMENT-PREPARER-MISSING",
                        "El pago histórico no identifica preparador",
                        409,
                    )
                if row.id_usuario_prepara == identity.id_usuario:
                    raise PaymentOperationError(
                        "PAYMENT-AUTHORIZE-FORBIDDEN",
                        "La misma persona no puede preparar y autorizar el pago",
                        403,
                    )
                critical_pending = session.scalar(
                    select(
                        exists().where(
                            Alerta.id_siniestro == row.id_siniestro,
                            Alerta.severidad == "critica",
                            Alerta.estado_revision == "pendiente",
                        )
                    )
                )
                if critical_pending:
                    raise PaymentOperationError(
                        "PAYMENT-BLOCKED-BY-CRITICAL-ALERT",
                        "Una alerta crítica pendiente requiere revisión humana",
                        409,
                    )
                now = datetime.now(timezone.utc)
                authorization = Autorizacion(
                    id_usuario_autoriza=identity.id_usuario,
                    fecha=now,
                    objeto_autorizado=f"pago:{row.id_pago}",
                )
                session.add(authorization)
                session.flush()
                row.id_autorizacion = authorization.id_autorizacion
                row.estado = PaymentStatus.EMITIDO.value
                row.version += 1
                preparer = self._subject_for_user(
                    session,
                    row.id_usuario_prepara,
                )
                result = PaymentRecord(
                    id=row.id_pago,
                    claim_id=row.id_siniestro,
                    amount=row.monto,
                    status=PaymentStatus(row.estado),
                    preparer_subject=preparer or "",
                    authorizer_subject=principal.subject,
                    version=row.version,
                )
                session.add(
                    EventoLineaTiempo(
                        id_siniestro=row.id_siniestro,
                        id_usuario=identity.id_usuario,
                        tipo_evento="pago_autorizado",
                        fecha=now,
                        detalle={
                            "id_pago": row.id_pago,
                            "id_autorizacion": authorization.id_autorizacion,
                            "monto": str(row.monto),
                            "estado": row.estado,
                            "simulado": True,
                            "transferencia_realizada": False,
                        },
                    )
                )
                session.add(
                    SolicitudAutorizacionPagoIdempotente(
                        clave=idempotency_key,
                        huella=fingerprint,
                        id_pago=row.id_pago,
                        respuesta=self._serialize(result),
                        creado_en=now,
                    )
                )
            return result
        except IntegrityError as exc:
            stored = self.find_authorize_request(idempotency_key)
            if stored is not None and stored.fingerprint == fingerprint:
                return stored.result
            if stored is not None:
                raise PaymentOperationError(
                    "IDEMPOTENCY-CONFLICT",
                    "Idempotency-Key ya fue utilizada con otro contenido",
                    409,
                ) from exc
            raise
