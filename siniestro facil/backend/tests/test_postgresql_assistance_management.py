import inspect

from siniestro_facil.persistence.assistance_repository import (
    PostgreSQLAssistanceRepository,
)


def test_reply_uses_lock_and_atomic_audit() -> None:
    source = inspect.getsource(
        PostgreSQLAssistanceRepository.register_reply
    )
    assert "with self._factory() as session, session.begin()" in source
    assert "with_for_update=True" in source
    assert "_check_expected_attempt" in source
    assert 'tipo_evento="respuesta_proveedor_registrada"' in source


def test_reassignment_preserves_history_and_audits() -> None:
    source = inspect.getsource(
        PostgreSQLAssistanceRepository.reassign
    )
    assert "with self._factory() as session, session.begin()" in source
    assert "with_for_update=True" in source
    assert "replacement = Asistencia(" in source
    assert "current.numero_intento + 1" in source
    assert 'tipo_evento="asistencia_reasignada"' in source
    assert "session.flush()" in source
