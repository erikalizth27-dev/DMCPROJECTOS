from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from siniestro_facil.application.assistance_contracts import AssistanceRecord
from siniestro_facil.domain.assistance import (
    AssistanceStatus,
    RetryPolicy,
)


PILOT_RETRY_POLICY = RetryPolicy(
    delays_seconds=(30, 120, 300),
    timeout_seconds=10,
)


class RetryAction(StrEnum):
    RETRY = "reintentar"
    ESCALATE = "escalar"


class RetryDecisionError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class RetryDecision:
    assistance_id: int
    action: RetryAction
    current_attempt: int
    next_attempt: int | None
    delay_seconds: int
    timeout_seconds: int
    reason: str


def decide_assistance_retry(
    assistance: AssistanceRecord,
    *,
    policy: RetryPolicy = PILOT_RETRY_POLICY,
) -> RetryDecision:
    if assistance.status not in {
        AssistanceStatus.NO_RESPONSE,
        AssistanceStatus.REJECTED,
    }:
        raise RetryDecisionError(
            "Solo se reintenta una asistencia rechazada o sin respuesta"
        )
    if assistance.attempt <= 0:
        raise RetryDecisionError("El número de intento es inválido")
    if assistance.attempt > policy.max_attempts:
        raise RetryDecisionError(
            "El intento excede la política aprobada"
        )

    delay = policy.delays_seconds[assistance.attempt - 1]
    if assistance.attempt == policy.max_attempts:
        return RetryDecision(
            assistance_id=assistance.id,
            action=RetryAction.ESCALATE,
            current_attempt=assistance.attempt,
            next_attempt=None,
            delay_seconds=delay,
            timeout_seconds=policy.timeout_seconds,
            reason="Tercer fallo del proveedor",
        )
    return RetryDecision(
        assistance_id=assistance.id,
        action=RetryAction.RETRY,
        current_attempt=assistance.attempt,
        next_attempt=assistance.attempt + 1,
        delay_seconds=delay,
        timeout_seconds=policy.timeout_seconds,
        reason="Proveedor rechazó o no respondió",
    )
