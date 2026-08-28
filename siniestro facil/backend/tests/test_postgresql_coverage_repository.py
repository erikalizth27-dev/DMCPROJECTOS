import inspect

from siniestro_facil.persistence.coverage_repository import (
    PostgreSQLCoverageRepository,
)


def test_repository_locks_claim_and_rechecks_version() -> None:
    source = inspect.getsource(
        PostgreSQLCoverageRepository.save_verification
    )
    assert ".with_for_update()" in source
    assert "claim.version != context.version" in source
    assert '"STATE-VERSION-CONFLICT"' in source


def test_repository_persists_coverage_transition_and_audit_atomically() -> None:
    source = inspect.getsource(
        PostgreSQLCoverageRepository.save_verification
    )
    assert "coverage.deducible = verification.deductible" in source
    assert "coverage.estado_validacion" in source
    assert "claim.estado_actual = verification.current_state.value" in source
    assert "claim.version = verification.version" in source
    assert 'tipo_evento="cobertura_verificada"' in source
    assert '"requiere_revision_humana"' in source
    assert '"adaptador": "simulado"' in source
