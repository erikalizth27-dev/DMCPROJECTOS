from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from siniestro_facil.application.manage_payment import (
    AuthorizePaymentCommand,
    AuthorizePaymentService,
    InMemoryPaymentRepository,
    PaymentOperationError,
    PreparePaymentCommand,
    PreparePaymentService,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import (
    ActorType,
    AuthenticatedPrincipal,
)
from siniestro_facil.domain.payment import PaymentStatus
from siniestro_facil.infrastructure.payment_adapter import (
    DeterministicPaymentAdapter,
)


def principal(
    role: PrincipalRole,
    *,
    subject: str | None = None,
) -> AuthenticatedPrincipal:
    now = datetime.now(timezone.utc)
    return AuthenticatedPrincipal(
        subject=subject or f"{role.value}-payment-service",
        role=role,
        actor_type=ActorType.INTERNO,
        tenant_id="tenant-synthetic",
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


def prepare(
    repository: InMemoryPaymentRepository,
    actor: AuthenticatedPrincipal | None = None,
    *,
    key: str = "payment-prepare-0001",
    amount: Decimal = Decimal("125.50"),
):
    actor = actor or principal(PrincipalRole.OPERADOR)
    payload = {"siniestroId": 42, "monto": str(amount)}
    return PreparePaymentService(repository).execute(
        PreparePaymentCommand(42, amount),
        actor,
        idempotency_key=key,
        request_payload=payload,
    )


def authorize(
    repository: InMemoryPaymentRepository,
    payment_id: int,
    actor: AuthenticatedPrincipal | None = None,
    *,
    key: str = "payment-authorize-0001",
    version: int = 0,
):
    actor = actor or principal(PrincipalRole.SUPERVISOR)
    return AuthorizePaymentService(
        repository,
        DeterministicPaymentAdapter(version="pilot-1"),
    ).execute(
        AuthorizePaymentCommand(42, payment_id, version),
        actor,
        idempotency_key=key,
        request_payload={
            "siniestroId": 42,
            "pagoId": payment_id,
            "version": version,
        },
    )


def test_operator_prepares_blocked_payment() -> None:
    repository = InMemoryPaymentRepository()
    result = prepare(repository)
    assert result.status is PaymentStatus.BLOQUEADO
    assert result.version == 0
    assert repository.audit_events[0][0] == "pago_preparado"


def test_adjuster_can_prepare_payment() -> None:
    repository = InMemoryPaymentRepository()
    result = prepare(repository, principal(PrincipalRole.AJUSTADOR))
    assert result.status is PaymentStatus.BLOQUEADO


def test_insured_cannot_prepare_payment() -> None:
    with pytest.raises(PaymentOperationError) as error:
        prepare(
            InMemoryPaymentRepository(),
            principal(PrincipalRole.ASEGURADO),
        )
    assert error.value.code == "PAYMENT-PREPARE-FORBIDDEN"
    assert error.value.status_code == 403


def test_prepare_repetition_is_idempotent() -> None:
    repository = InMemoryPaymentRepository()
    first = prepare(repository)
    repeated = prepare(repository)
    assert repeated == first
    assert len(repository.audit_events) == 1


def test_prepare_changed_content_conflicts() -> None:
    repository = InMemoryPaymentRepository()
    prepare(repository)
    with pytest.raises(PaymentOperationError) as error:
        prepare(repository, amount=Decimal("200.00"))
    assert error.value.code == "IDEMPOTENCY-CONFLICT"


def test_supervisor_authorizes_without_real_transfer() -> None:
    repository = InMemoryPaymentRepository()
    payment = prepare(repository)
    result = authorize(repository, payment.id)
    assert result.status is PaymentStatus.EMITIDO
    assert result.version == 1
    assert result.money_transferred is False
    assert repository.audit_events[-1][0] == "pago_autorizado"


def test_operator_cannot_authorize() -> None:
    repository = InMemoryPaymentRepository()
    payment = prepare(repository)
    with pytest.raises(PaymentOperationError) as error:
        authorize(
            repository,
            payment.id,
            principal(PrincipalRole.OPERADOR, subject="operator-2"),
        )
    assert error.value.code == "PAYMENT-AUTHORIZE-FORBIDDEN"


def test_same_person_cannot_prepare_and_authorize() -> None:
    repository = InMemoryPaymentRepository()
    supervisor = principal(
        PrincipalRole.SUPERVISOR,
        subject="supervisor-same",
    )
    payment = prepare(repository, supervisor)
    with pytest.raises(PaymentOperationError) as error:
        authorize(repository, payment.id, supervisor)
    assert error.value.code == "PAYMENT-AUTHORIZE-FORBIDDEN"


def test_pending_critical_alert_blocks_payment() -> None:
    repository = InMemoryPaymentRepository(
        critical_alert_claims={42}
    )
    payment = prepare(repository)
    with pytest.raises(PaymentOperationError) as error:
        authorize(repository, payment.id)
    assert error.value.code == "PAYMENT-BLOCKED-BY-CRITICAL-ALERT"
    assert repository.get(42, payment.id).status is PaymentStatus.BLOQUEADO


def test_stale_payment_version_conflicts() -> None:
    repository = InMemoryPaymentRepository()
    payment = prepare(repository)
    authorize(repository, payment.id)
    with pytest.raises(PaymentOperationError) as error:
        authorize(
            repository,
            payment.id,
            key="payment-authorize-0002",
            version=0,
        )
    assert error.value.code == "PAYMENT-VERSION-CONFLICT"


def test_authorization_repetition_is_idempotent() -> None:
    repository = InMemoryPaymentRepository()
    payment = prepare(repository)
    first = authorize(repository, payment.id)
    repeated = authorize(repository, payment.id)
    assert repeated == first
    assert [event[0] for event in repository.audit_events].count(
        "pago_autorizado"
    ) == 1
