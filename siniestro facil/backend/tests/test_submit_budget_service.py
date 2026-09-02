from datetime import date, datetime, timedelta, timezone

import pytest

from siniestro_facil.application.submit_budget import (
    BudgetSubmissionError,
    GetBudgetService,
    InMemoryBudgetSubmissionRepository,
    SubmitBudgetCommand,
    SubmitBudgetService,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal


def principal(role: PrincipalRole = PrincipalRole.TALLER) -> AuthenticatedPrincipal:
    now = datetime.now(timezone.utc)
    actor_type = (
        ActorType.PROVEEDOR
        if role is PrincipalRole.TALLER
        else ActorType.INTERNO
    )
    return AuthenticatedPrincipal(
        subject=f"{role.value}-budget-synthetic",
        role=role,
        actor_type=actor_type,
        tenant_id="tenant-synthetic",
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


def command() -> SubmitBudgetCommand:
    return SubmitBudgetCommand(
        claim_id=42,
        inspection_id=7,
        diagnosis="Daño frontal sujeto a revisión",
        presented_on=date(2026, 9, 2),
        expected_version=4,
    )


def test_taller_submits_budget_with_approved_validity() -> None:
    result = SubmitBudgetService(
        InMemoryBudgetSubmissionRepository()
    ).execute(command(), principal())

    assert result.claim_id == 42
    assert result.inspection_id == 7
    assert result.diagnosis == command().diagnosis
    assert result.valid_from == date(2026, 9, 2)
    assert result.valid_until == date(2026, 9, 17)
    assert result.status.value == "recibido"
    assert result.current_state.value == "presupuesto_recibido"
    assert result.version == 5


def test_rejects_non_taller_role() -> None:
    with pytest.raises(BudgetSubmissionError) as caught:
        SubmitBudgetService(
            InMemoryBudgetSubmissionRepository()
        ).execute(command(), principal(PrincipalRole.OPERADOR))

    assert caught.value.code == "BUDGET-FORBIDDEN"
    assert caught.value.status_code == 403


def test_requires_diagnosis() -> None:
    invalid = SubmitBudgetCommand(
        claim_id=42,
        inspection_id=7,
        diagnosis=" ",
        presented_on=date(2026, 9, 2),
        expected_version=4,
    )
    with pytest.raises(BudgetSubmissionError) as caught:
        SubmitBudgetService(
            InMemoryBudgetSubmissionRepository()
        ).execute(invalid, principal())

    assert caught.value.code == "BUDGET-DIAGNOSIS-REQUIRED"


def test_rejects_invalid_identifiers_or_version() -> None:
    invalid = SubmitBudgetCommand(
        claim_id=0,
        inspection_id=7,
        diagnosis="Diagnóstico",
        presented_on=date(2026, 9, 2),
        expected_version=-1,
    )
    with pytest.raises(BudgetSubmissionError) as caught:
        SubmitBudgetService(
            InMemoryBudgetSubmissionRepository()
        ).execute(invalid, principal())

    assert caught.value.code == "BUDGET-REQUEST-INVALID"


def test_get_returns_submitted_budget() -> None:
    repository = InMemoryBudgetSubmissionRepository()
    submitted = SubmitBudgetService(repository).execute(command(), principal())

    assert GetBudgetService(repository).execute(
        42, submitted.id, principal()
    ) == submitted


def test_get_hides_unrelated_budget() -> None:
    repository = InMemoryBudgetSubmissionRepository()
    submitted = SubmitBudgetService(repository).execute(command(), principal())

    with pytest.raises(BudgetSubmissionError) as caught:
        GetBudgetService(repository).execute(99, submitted.id, principal())

    assert caught.value.code == "BUDGET-NOT-FOUND"
    assert caught.value.status_code == 404
