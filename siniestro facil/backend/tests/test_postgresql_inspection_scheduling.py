import inspect

from siniestro_facil.persistence.inspection_budget_repository import (
    PostgreSQLInspectionSchedulingRepository,
)


def scheduling_source() -> str:
    return inspect.getsource(
        PostgreSQLInspectionSchedulingRepository.schedule
    )


def test_schedule_requires_active_assignment_and_internal_identity() -> None:
    source = scheduling_source()
    assert "_internal_identity_in_scope" in source
    assert '"INSPECTION-NOT-FOUND"' in source


def test_schedule_locks_claim_and_checks_version() -> None:
    source = scheduling_source()
    assert ".with_for_update()" in source
    assert "claim.version != command.expected_version" in source
    assert '"STATE-VERSION-CONFLICT"' in source


def test_schedule_validates_state_transition() -> None:
    source = scheduling_source()
    assert "validar_transicion(" in source
    assert "EstadoSiniestro.INSPECCION_PROGRAMADA" in source
    assert '"INVALID-TRANSITION"' in source


def test_schedule_persists_inspection_state_and_audit_atomically() -> None:
    source = scheduling_source()
    assert "with self._factory() as session, session.begin()" in source
    assert "inspection = Inspeccion(" in source
    assert "claim.estado_actual =" in source
    assert "claim.version += 1" in source
    assert 'tipo_evento="inspeccion_programada"' in source
    assert "session.flush()" in source


def test_get_enforces_scope_and_claim_relationship() -> None:
    source = inspect.getsource(
        PostgreSQLInspectionSchedulingRepository.get
    )
    assert "_internal_identity_in_scope" in source
    assert "inspection.id_siniestro != claim_id" in source
    assert "session.get(Siniestro, claim_id)" in source
