from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from enum import StrEnum

from siniestro_facil.domain.authorization import PrincipalRole


PILOT_BUDGET_VALIDITY_DAYS = 15


class BudgetStatus(StrEnum):
    RECEIVED = "recibido"
    OBSERVED = "observado"
    AUTHORIZED = "autorizado"
    REJECTED = "rechazado"


class BudgetDecisionDenied(PermissionError):
    pass


def budget_valid_until(presented_on: date) -> date:
    return presented_on + timedelta(days=PILOT_BUDGET_VALIDITY_DAYS)


def budget_is_expired(
    *,
    valid_until: date,
    evaluated_on: date,
) -> bool:
    return evaluated_on > valid_until


@dataclass(frozen=True, slots=True)
class BudgetDecision:
    role: PrincipalRole
    target: BudgetStatus
    actor_assigned: bool


def validate_budget_decision(decision: BudgetDecision) -> None:
    if decision.target is BudgetStatus.OBSERVED:
        if decision.role not in {
            PrincipalRole.OPERADOR,
            PrincipalRole.AJUSTADOR,
        }:
            raise BudgetDecisionDenied(
                "Solo operador o ajustador puede observar"
            )
        if not decision.actor_assigned:
            raise BudgetDecisionDenied(
                "El operador o ajustador debe estar asignado al caso"
            )
        return

    if decision.target in {
        BudgetStatus.AUTHORIZED,
        BudgetStatus.REJECTED,
    }:
        if decision.role is not PrincipalRole.SUPERVISOR:
            raise BudgetDecisionDenied(
                "Solo supervisor puede aprobar o rechazar"
            )
        return

    raise BudgetDecisionDenied("La decisión solicitada no es válida")
