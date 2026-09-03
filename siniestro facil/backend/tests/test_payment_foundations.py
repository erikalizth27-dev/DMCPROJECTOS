from decimal import Decimal

import pytest

from siniestro_facil.domain.authorization import (
    PaymentApproval,
    PrincipalRole,
)
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


def test_prepared_payment_starts_blocked() -> None:
    assert initial_payment_status() is PaymentStatus.BLOQUEADO


def test_payment_request_requires_positive_amount() -> None:
    with pytest.raises(ValueError, match="mayor que cero"):
        PaymentRequest(4, Decimal("0"), "operator-1")


def test_payment_request_requires_preparer() -> None:
    with pytest.raises(ValueError, match="preparador"):
        PaymentRequest(4, Decimal("10.00"), "   ")


def test_supervisor_different_from_preparer_can_authorize() -> None:
    context = PaymentAuthorizationContext(
        approval=PaymentApproval(
            preparer_id="operator-1",
            authorizer_id="supervisor-1",
            authorizer_role=PrincipalRole.SUPERVISOR,
        ),
        critical_alert_pending=False,
    )
    assert authorize_payment(context) is PaymentStatus.EMITIDO


def test_critical_pending_alert_blocks_authorization() -> None:
    context = PaymentAuthorizationContext(
        approval=PaymentApproval(
            preparer_id="operator-1",
            authorizer_id="supervisor-1",
            authorizer_role=PrincipalRole.SUPERVISOR,
        ),
        critical_alert_pending=True,
    )
    with pytest.raises(PaymentBlocked, match="revisión humana"):
        authorize_payment(context)


def test_simulated_adapter_never_transfers_money() -> None:
    adapter = DeterministicPaymentAdapter(version="pilot-1")
    result = adapter.emit(payment_id=9, amount=Decimal("125.50"))
    assert result.status is PaymentStatus.EMITIDO
    assert result.simulated is True
    assert result.money_transferred is False
    assert result.adapter_version == "pilot-1"


def test_simulated_adapter_requires_version() -> None:
    with pytest.raises(ValueError, match="versión"):
        DeterministicPaymentAdapter(version=" ")
