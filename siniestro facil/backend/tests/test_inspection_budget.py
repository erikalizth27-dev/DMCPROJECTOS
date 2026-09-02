from datetime import date, timedelta

import pytest

from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.inspection_budget import (
    PILOT_BUDGET_VALIDITY_DAYS,
    BudgetDecision,
    BudgetDecisionDenied,
    BudgetStatus,
    budget_is_expired,
    budget_valid_until,
    validate_budget_decision,
)


def test_budget_validity_is_fifteen_calendar_days() -> None:
    presented = date(2026, 9, 2)

    assert PILOT_BUDGET_VALIDITY_DAYS == 15
    assert budget_valid_until(presented) == date(2026, 9, 17)


@pytest.mark.parametrize("elapsed_days", [14, 15])
def test_budget_remains_valid_through_end_date(
    elapsed_days: int,
) -> None:
    presented = date(2026, 9, 2)

    assert not budget_is_expired(
        valid_until=budget_valid_until(presented),
        evaluated_on=presented + timedelta(days=elapsed_days),
    )


def test_budget_expires_after_end_date() -> None:
    presented = date(2026, 9, 2)

    assert budget_is_expired(
        valid_until=budget_valid_until(presented),
        evaluated_on=presented + timedelta(days=16),
    )


@pytest.mark.parametrize(
    "role",
    [PrincipalRole.OPERADOR, PrincipalRole.AJUSTADOR],
)
def test_assigned_operator_or_adjuster_can_observe(
    role: PrincipalRole,
) -> None:
    validate_budget_decision(
        BudgetDecision(
            role=role,
            target=BudgetStatus.OBSERVED,
            actor_assigned=True,
        )
    )


@pytest.mark.parametrize(
    "target",
    [BudgetStatus.AUTHORIZED, BudgetStatus.REJECTED],
)
def test_supervisor_can_approve_or_reject(
    target: BudgetStatus,
) -> None:
    validate_budget_decision(
        BudgetDecision(
            role=PrincipalRole.SUPERVISOR,
            target=target,
            actor_assigned=False,
        )
    )


@pytest.mark.parametrize(
    "role",
    [
        PrincipalRole.OPERADOR,
        PrincipalRole.AJUSTADOR,
        PrincipalRole.TALLER,
    ],
)
def test_non_supervisor_cannot_approve(
    role: PrincipalRole,
) -> None:
    with pytest.raises(BudgetDecisionDenied, match="Solo supervisor"):
        validate_budget_decision(
            BudgetDecision(
                role=role,
                target=BudgetStatus.AUTHORIZED,
                actor_assigned=True,
            )
        )


def test_unassigned_observer_is_denied() -> None:
    with pytest.raises(BudgetDecisionDenied, match="asignado"):
        validate_budget_decision(
            BudgetDecision(
                role=PrincipalRole.OPERADOR,
                target=BudgetStatus.OBSERVED,
                actor_assigned=False,
            )
        )
