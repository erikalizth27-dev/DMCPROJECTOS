from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from siniestro_facil.domain.payment import PaymentStatus


@dataclass(frozen=True, slots=True)
class SimulatedPaymentResult:
    payment_id: int
    amount: Decimal
    status: PaymentStatus
    adapter_version: str
    simulated: bool
    money_transferred: bool


class DeterministicPaymentAdapter:
    """Adaptador piloto sin comunicación ni transferencia monetaria externa."""

    def __init__(self, *, version: str) -> None:
        if not version.strip():
            raise ValueError("La versión del adaptador es obligatoria")
        self._version = version.strip()

    @property
    def version(self) -> str:
        return self._version

    def emit(
        self,
        *,
        payment_id: int,
        amount: Decimal,
    ) -> SimulatedPaymentResult:
        if payment_id <= 0:
            raise ValueError("El pago es obligatorio")
        if amount <= Decimal("0"):
            raise ValueError("El monto debe ser mayor que cero")
        return SimulatedPaymentResult(
            payment_id=payment_id,
            amount=amount,
            status=PaymentStatus.EMITIDO,
            adapter_version=self._version,
            simulated=True,
            money_transferred=False,
        )
