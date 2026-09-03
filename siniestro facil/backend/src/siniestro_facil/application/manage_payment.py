from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from typing import Protocol

from siniestro_facil.domain.authorization import (
    Action,
    AuthorizationDenied,
    PaymentApproval,
    authorize,
)
from siniestro_facil.domain.idempotency import (
    fingerprint_request,
    validate_idempotency_key,
)
from siniestro_facil.domain.identity import AuthenticatedPrincipal
from siniestro_facil.domain.payment import (
    PaymentAuthorizationContext,
    PaymentBlocked,
    PaymentRequest,
    PaymentStatus,
    authorize_payment,
    initial_payment_status,
)
from siniestro_facil.infrastructure.payment_adapter import (
    DeterministicPaymentAdapter,
)


class PaymentOperationError(RuntimeError):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


@dataclass(frozen=True, slots=True)
class PreparePaymentCommand:
    claim_id: int
    amount: Decimal


@dataclass(frozen=True, slots=True)
class AuthorizePaymentCommand:
    claim_id: int
    payment_id: int
    expected_version: int


@dataclass(frozen=True, slots=True)
class PaymentRecord:
    id: int
    claim_id: int
    amount: Decimal
    status: PaymentStatus
    preparer_subject: str
    authorizer_subject: str | None
    version: int
    simulated: bool = True
    money_transferred: bool = False


@dataclass(frozen=True, slots=True)
class StoredPaymentRequest:
    fingerprint: str
    result: PaymentRecord


class PaymentRepository(Protocol):
    def find_prepare_request(
        self, idempotency_key: str
    ) -> StoredPaymentRequest | None: ...

    def prepare(
        self,
        request: PaymentRequest,
        *,
        idempotency_key: str,
        fingerprint: str,
    ) -> PaymentRecord: ...

    def find_authorize_request(
        self, idempotency_key: str
    ) -> StoredPaymentRequest | None: ...

    def get(self, claim_id: int, payment_id: int) -> PaymentRecord | None: ...

    def has_pending_critical_alert(self, claim_id: int) -> bool: ...

    def authorize(
        self,
        payment: PaymentRecord,
        principal: AuthenticatedPrincipal,
        *,
        idempotency_key: str,
        fingerprint: str,
    ) -> PaymentRecord: ...


class InMemoryPaymentRepository:
    def __init__(
        self,
        *,
        critical_alert_claims: set[int] | None = None,
    ) -> None:
        self._next_id = 1
        self._payments: dict[int, PaymentRecord] = {}
        self._prepare_requests: dict[str, StoredPaymentRequest] = {}
        self._authorize_requests: dict[str, StoredPaymentRequest] = {}
        self._critical_alert_claims = set(critical_alert_claims or ())
        self.audit_events: list[tuple[str, int, str]] = []

    def find_prepare_request(
        self, idempotency_key: str
    ) -> StoredPaymentRequest | None:
        return self._prepare_requests.get(idempotency_key)

    def prepare(
        self,
        request: PaymentRequest,
        *,
        idempotency_key: str,
        fingerprint: str,
    ) -> PaymentRecord:
        result = PaymentRecord(
            id=self._next_id,
            claim_id=request.claim_id,
            amount=request.amount,
            status=initial_payment_status(),
            preparer_subject=request.preparer_subject,
            authorizer_subject=None,
            version=0,
        )
        self._payments[result.id] = result
        self._prepare_requests[idempotency_key] = StoredPaymentRequest(
            fingerprint, result
        )
        self.audit_events.append(
            ("pago_preparado", result.id, request.preparer_subject)
        )
        self._next_id += 1
        return result

    def find_authorize_request(
        self, idempotency_key: str
    ) -> StoredPaymentRequest | None:
        return self._authorize_requests.get(idempotency_key)

    def get(self, claim_id: int, payment_id: int) -> PaymentRecord | None:
        payment = self._payments.get(payment_id)
        if payment is None or payment.claim_id != claim_id:
            return None
        return payment

    def has_pending_critical_alert(self, claim_id: int) -> bool:
        return claim_id in self._critical_alert_claims

    def authorize(
        self,
        payment: PaymentRecord,
        principal: AuthenticatedPrincipal,
        *,
        idempotency_key: str,
        fingerprint: str,
    ) -> PaymentRecord:
        current = self.get(payment.claim_id, payment.id)
        if current is None:
            raise PaymentOperationError(
                "PAYMENT-NOT-FOUND",
                "Pago no encontrado",
                404,
            )
        if current.version != payment.version:
            raise PaymentOperationError(
                "PAYMENT-VERSION-CONFLICT",
                "El pago fue modificado por otra operación",
                409,
            )
        if current.status is PaymentStatus.EMITIDO:
            raise PaymentOperationError(
                "PAYMENT-ALREADY-AUTHORIZED",
                "El pago ya fue autorizado",
                409,
            )
        result = replace(
            current,
            status=PaymentStatus.EMITIDO,
            authorizer_subject=principal.subject,
            version=current.version + 1,
        )
        self._payments[result.id] = result
        self._authorize_requests[idempotency_key] = StoredPaymentRequest(
            fingerprint, result
        )
        self.audit_events.append(
            ("pago_autorizado", result.id, principal.subject)
        )
        return result


def _idempotency(
    repository_result: StoredPaymentRequest | None,
    *,
    fingerprint: str,
) -> PaymentRecord | None:
    if repository_result is None:
        return None
    if repository_result.fingerprint != fingerprint:
        raise PaymentOperationError(
            "IDEMPOTENCY-CONFLICT",
            "Idempotency-Key ya fue utilizada con otro contenido",
            409,
        )
    return repository_result.result


class PreparePaymentService:
    def __init__(self, repository: PaymentRepository) -> None:
        self._repository = repository

    def execute(
        self,
        command: PreparePaymentCommand,
        principal: AuthenticatedPrincipal,
        *,
        idempotency_key: str,
        request_payload: object,
    ) -> PaymentRecord:
        try:
            authorize(
                principal.role,
                Action.PREPARAR_PAGO,
                resource_in_scope=True,
            )
        except AuthorizationDenied as exc:
            raise PaymentOperationError(
                "PAYMENT-PREPARE-FORBIDDEN",
                "Acción no permitida para el rol",
                403,
            ) from exc
        try:
            request = PaymentRequest(
                claim_id=command.claim_id,
                amount=command.amount,
                preparer_subject=principal.subject,
            )
            key = validate_idempotency_key(idempotency_key)
        except ValueError as exc:
            raise PaymentOperationError(
                "PAYMENT-PREPARE-INVALID",
                str(exc),
                422,
            ) from exc
        fingerprint = fingerprint_request(request_payload)
        existing = _idempotency(
            self._repository.find_prepare_request(key),
            fingerprint=fingerprint,
        )
        if existing is not None:
            return existing
        return self._repository.prepare(
            request,
            idempotency_key=key,
            fingerprint=fingerprint,
        )


class AuthorizePaymentService:
    def __init__(
        self,
        repository: PaymentRepository,
        adapter: DeterministicPaymentAdapter,
    ) -> None:
        self._repository = repository
        self._adapter = adapter

    def execute(
        self,
        command: AuthorizePaymentCommand,
        principal: AuthenticatedPrincipal,
        *,
        idempotency_key: str,
        request_payload: object,
    ) -> PaymentRecord:
        try:
            authorize(
                principal.role,
                Action.AUTORIZAR_PAGO,
                resource_in_scope=True,
            )
        except AuthorizationDenied as exc:
            raise PaymentOperationError(
                "PAYMENT-AUTHORIZE-FORBIDDEN",
                "Solo un supervisor puede autorizar pagos",
                403,
            ) from exc
        if (
            command.claim_id <= 0
            or command.payment_id <= 0
            or command.expected_version < 0
        ):
            raise PaymentOperationError(
                "PAYMENT-AUTHORIZE-INVALID",
                "Siniestro, pago o versión inválidos",
                422,
            )
        try:
            key = validate_idempotency_key(idempotency_key)
        except ValueError as exc:
            raise PaymentOperationError(
                "PAYMENT-AUTHORIZE-INVALID",
                str(exc),
                422,
            ) from exc
        fingerprint = fingerprint_request(request_payload)
        existing = _idempotency(
            self._repository.find_authorize_request(key),
            fingerprint=fingerprint,
        )
        if existing is not None:
            return existing
        payment = self._repository.get(
            command.claim_id,
            command.payment_id,
        )
        if payment is None:
            raise PaymentOperationError(
                "PAYMENT-NOT-FOUND",
                "Pago no encontrado",
                404,
            )
        if payment.version != command.expected_version:
            raise PaymentOperationError(
                "PAYMENT-VERSION-CONFLICT",
                "El pago fue modificado por otra operación",
                409,
            )
        try:
            authorize_payment(
                PaymentAuthorizationContext(
                    approval=PaymentApproval(
                        preparer_id=payment.preparer_subject,
                        authorizer_id=principal.subject,
                        authorizer_role=principal.role,
                    ),
                    critical_alert_pending=(
                        self._repository.has_pending_critical_alert(
                            command.claim_id
                        )
                    ),
                )
            )
        except PaymentBlocked as exc:
            raise PaymentOperationError(
                "PAYMENT-BLOCKED-BY-CRITICAL-ALERT",
                str(exc),
                409,
            ) from exc
        except AuthorizationDenied as exc:
            raise PaymentOperationError(
                "PAYMENT-AUTHORIZE-FORBIDDEN",
                str(exc),
                403,
            ) from exc
        simulation = self._adapter.emit(
            payment_id=payment.id,
            amount=payment.amount,
        )
        if simulation.money_transferred:
            raise PaymentOperationError(
                "PAYMENT-ADAPTER-UNSAFE",
                "El adaptador piloto no puede transferir dinero",
                500,
            )
        return self._repository.authorize(
            payment,
            principal,
            idempotency_key=key,
            fingerprint=fingerprint,
        )
