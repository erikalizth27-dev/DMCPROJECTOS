import inspect

from siniestro_facil.persistence.assistance_repository import (
    PostgreSQLAssistanceRepository,
)


def test_repository_persists_request_audit_and_idempotency() -> None:
    source = inspect.getsource(PostgreSQLAssistanceRepository.create)
    assert "with self._factory() as session, session.begin()" in source
    assert "Asistencia(" in source
    assert 'tipo_evento="asistencia_solicitada"' in source
    assert "SolicitudAsistenciaIdempotente(" in source
    assert "session.flush()" in source


def test_repository_persists_dispatch_and_audit() -> None:
    source = inspect.getsource(
        PostgreSQLAssistanceRepository.mark_sent
    )
    assert "with self._factory() as session, session.begin()" in source
    assert "with_for_update=True" in source
    assert "referencia_externa" in source
    assert 'tipo_evento="asistencia_enviada"' in source
    assert "request.respuesta" in source
