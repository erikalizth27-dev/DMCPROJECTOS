import inspect

from siniestro_facil.persistence.inspection_budget_repository import (
    PostgreSQLBudgetDecisionRepository,
)


def decision_source() -> str:
    return inspect.getsource(PostgreSQLBudgetDecisionRepository.decide)


def test_repository_enforces_identity_assignment_and_role() -> None:
    source = decision_source()
    assert "_internal_identity_in_scope" in source
    assert "identity.id_usuario is None" in source
    assert "validate_budget_decision(" in source


def test_repository_locks_budget_claim_and_checks_version() -> None:
    source = decision_source()
    assert "with_for_update=True" in source
    assert ".with_for_update()" in source
    assert "claim.version != command.expected_version" in source
    assert '"STATE-VERSION-CONFLICT"' in source


def test_repository_prevents_authorizing_expired_budget() -> None:
    source = decision_source()
    assert "BudgetStatus.AUTHORIZED" in source
    assert "budget_is_expired(" in source
    assert '"BUDGET-EXPIRED"' in source


def test_repository_persists_authorization_change_and_audit() -> None:
    source = decision_source()
    assert "with self._factory() as session, session.begin()" in source
    assert "authorization = Autorizacion(" in source
    assert "change = CambioPresupuesto(" in source
    assert "budget.estado = command.target.value" in source
    assert "claim.version += 1" in source
    assert 'tipo_evento="decision_presupuesto_registrada"' in source


def test_repository_persists_idempotency_and_handles_conflict() -> None:
    source = decision_source()
    assert "SolicitudDecisionPresupuestoIdempotente(" in source
    assert "existing.huella == command.fingerprint" in source
    assert '"IDEMPOTENCY-CONFLICT"' in source
    assert "except IntegrityError as exc" in source
