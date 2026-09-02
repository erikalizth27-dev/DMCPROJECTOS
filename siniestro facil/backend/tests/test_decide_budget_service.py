from datetime import datetime, timedelta, timezone

import pytest

from siniestro_facil.application.decide_budget import (
    BudgetDecisionError,
    DecideBudgetCommand,
    DecideBudgetService,
    InMemoryBudgetDecisionRepository,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal
from siniestro_facil.domain.inspection_budget import BudgetStatus


def principal(role: PrincipalRole) -> AuthenticatedPrincipal:
    now = datetime.now(timezone.utc)
    return AuthenticatedPrincipal(
        subject=f"{role.value}-decision-synthetic",
        role=role,
        actor_type=ActorType.INTERNO,
        tenant_id="tenant-synthetic",
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


def command(target: BudgetStatus) -> DecideBudgetCommand:
    return DecideBudgetCommand(
        claim_id=42,
        budget_id=7,
        target=target,
        reason="Decisión formal documentada",
        expected_version=5,
    )


@pytest.mark.parametrize(
    ("role", "target", "state"),
    [
        (PrincipalRole.OPERADOR, BudgetStatus.OBSERVED, "observado"),
        (PrincipalRole.AJUSTADOR, BudgetStatus.OBSERVED, "observado"),
        (PrincipalRole.SUPERVISOR, BudgetStatus.AUTHORIZED, "autorizado"),
        (PrincipalRole.SUPERVISOR, BudgetStatus.REJECTED, "rechazado"),
    ],
)
def test_authorized_decision_changes_contractual_state(
    role: PrincipalRole,
    target: BudgetStatus,
    state: str,
) -> None:
    result = DecideBudgetService(
        InMemoryBudgetDecisionRepository()
    ).execute(command(target), principal(role))

    assert result.target is target
    assert result.current_state.value == state
    assert result.reason == "Decisión formal documentada"
    assert result.version == 6


def test_operator_cannot_authorize() -> None:
    with pytest.raises(BudgetDecisionError) as caught:
        DecideBudgetService(
            InMemoryBudgetDecisionRepository()
        ).execute(
            command(BudgetStatus.AUTHORIZED),
            principal(PrincipalRole.OPERADOR),
        )

    assert caught.value.code == "BUDGET-DECISION-FORBIDDEN"
    assert caught.value.status_code == 403


def test_supervisor_cannot_record_observation() -> None:
    with pytest.raises(BudgetDecisionError) as caught:
        DecideBudgetService(
            InMemoryBudgetDecisionRepository()
        ).execute(
            command(BudgetStatus.OBSERVED),
            principal(PrincipalRole.SUPERVISOR),
        )

    assert caught.value.code == "BUDGET-DECISION-FORBIDDEN"


def test_requires_reason() -> None:
    invalid = DecideBudgetCommand(
        claim_id=42,
        budget_id=7,
        target=BudgetStatus.AUTHORIZED,
        reason=" ",
        expected_version=5,
    )
    with pytest.raises(BudgetDecisionError) as caught:
        DecideBudgetService(
            InMemoryBudgetDecisionRepository()
        ).execute(invalid, principal(PrincipalRole.SUPERVISOR))

    assert caught.value.code == "BUDGET-DECISION-REASON-REQUIRED"


def test_received_is_not_a_decision() -> None:
    with pytest.raises(BudgetDecisionError) as caught:
        DecideBudgetService(
            InMemoryBudgetDecisionRepository()
        ).execute(
            command(BudgetStatus.RECEIVED),
            principal(PrincipalRole.SUPERVISOR),
        )

    assert caught.value.code == "BUDGET-DECISION-FORBIDDEN"
