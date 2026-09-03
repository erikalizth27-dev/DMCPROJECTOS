from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from siniestro_facil.domain.authorization import (
    PaymentApproval,
    validate_payment_approval,
)


class PaymentStatus(StrEnum):
    BLOQUEADO = "bloqueado"
    EMITIDO = "emitido"


class PaymentBlocked(PermissionError):
    """El pago requiere una condición humana pendiente."""


@dataclass(frozen=True, slots=True)
class PaymentRequest:
    claim_id: int
    amount: Decimal
    preparer_subject: str

    def __post_init__(self) -> None:
        if self.claim_id <= 0:
            raise ValueError("El siniestro es obligatorio")
        if self.amount <= Decimal("0"):
            raise ValueError("El monto debe ser mayor que cero")
        if not self.preparer_subject.strip():
            raise ValueError("El preparador es obligatorio")


@dataclass(frozen=True, slots=True)
class PaymentAuthorizationContext:
    approval: PaymentApproval
    critical_alert_pending: bool


def initial_payment_status() -> PaymentStatus:
    return PaymentStatus.BLOQUEADO


def authorize_payment(
    context: PaymentAuthorizationContext,
) -> PaymentStatus:
    validate_payment_approval(context.approval)
    if context.critical_alert_pending:
        raise PaymentBlocked(
            "Una alerta crítica pendiente requiere revisión humana"
        )
    return PaymentStatus.EMITIDO
