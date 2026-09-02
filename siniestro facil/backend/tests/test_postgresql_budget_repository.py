import inspect

from siniestro_facil.persistence.inspection_budget_repository import (
    PostgreSQLBudgetSubmissionRepository,
)


def submit_source() -> str:
    return inspect.getsource(PostgreSQLBudgetSubmissionRepository.submit)


def test_repository_resolves_taller_provider_identity() -> None:
    source = submit_source()
    assert "_provider_identity" in source
    assert "identity.id_proveedor" in source
    assert "PrincipalRole.TALLER" in inspect.getsource(
        PostgreSQLBudgetSubmissionRepository._provider_identity
    )


def test_repository_locks_inspection_and_claim() -> None:
    source = submit_source()
    assert "with_for_update=True" in source
    assert ".with_for_update()" in source
    assert "claim.version != command.expected_version" in source
    assert '"STATE-VERSION-CONFLICT"' in source


def test_repository_links_budget_and_applies_validity() -> None:
    source = submit_source()
    assert "id_inspeccion=inspection.id_inspeccion" in source
    assert "budget_valid_until(" in source
    assert "BudgetStatus.RECEIVED.value" in source


def test_repository_persists_transition_audit_and_idempotency() -> None:
    source = submit_source()
    assert "with self._factory() as session, session.begin()" in source
    assert "claim.estado_actual =" in source
    assert "claim.version += 1" in source
    assert 'tipo_evento="presupuesto_presentado"' in source
    assert "SolicitudPresupuestoIdempotente(" in source
    assert "session.flush()" in source


def test_repository_handles_idempotent_repeat_and_conflict() -> None:
    source = submit_source()
    assert "existing.huella == command.fingerprint" in source
    assert '"IDEMPOTENCY-CONFLICT"' in source
    assert "except IntegrityError as exc" in source
