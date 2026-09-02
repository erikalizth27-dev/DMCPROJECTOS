from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class AssistanceStatus(StrEnum):
    PENDING = "pendiente"
    SENT = "enviada"
    ACCEPTED = "aceptada"
    REJECTED = "rechazada"
    NO_RESPONSE = "sin_respuesta"
    ESCALATED = "escalada"
    CANCELLED = "cancelada"


class ProviderResult(StrEnum):
    ACCEPTED = "aceptada"
    REJECTED = "rechazada"
    NO_RESPONSE = "sin_respuesta"


class InvalidAssistanceTransition(ValueError):
    pass


_ALLOWED_TRANSITIONS: dict[AssistanceStatus, frozenset[AssistanceStatus]] = {
    AssistanceStatus.PENDING: frozenset(
        {AssistanceStatus.SENT, AssistanceStatus.CANCELLED}
    ),
    AssistanceStatus.SENT: frozenset(
        {
            AssistanceStatus.ACCEPTED,
            AssistanceStatus.REJECTED,
            AssistanceStatus.NO_RESPONSE,
            AssistanceStatus.CANCELLED,
        }
    ),
    AssistanceStatus.NO_RESPONSE: frozenset(
        {
            AssistanceStatus.SENT,
            AssistanceStatus.ESCALATED,
            AssistanceStatus.CANCELLED,
        }
    ),
    AssistanceStatus.REJECTED: frozenset(
        {AssistanceStatus.SENT, AssistanceStatus.ESCALATED}
    ),
    AssistanceStatus.ACCEPTED: frozenset(),
    AssistanceStatus.ESCALATED: frozenset(),
    AssistanceStatus.CANCELLED: frozenset(),
}


def validate_assistance_transition(
    current: AssistanceStatus,
    target: AssistanceStatus,
) -> None:
    if target not in _ALLOWED_TRANSITIONS[current]:
        raise InvalidAssistanceTransition(
            f"Transición de asistencia no permitida: {current} -> {target}"
        )


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    delays_seconds: tuple[int, ...]
    timeout_seconds: int

    def __post_init__(self) -> None:
        if not self.delays_seconds:
            raise ValueError("La política requiere al menos un intento")
        if any(delay <= 0 for delay in self.delays_seconds):
            raise ValueError("Cada espera debe ser mayor que cero")
        if self.timeout_seconds <= 0:
            raise ValueError("El timeout debe ser mayor que cero")

    @property
    def max_attempts(self) -> int:
        return len(self.delays_seconds)
