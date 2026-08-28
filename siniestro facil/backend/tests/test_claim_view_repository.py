import inspect

from siniestro_facil.persistence.claim_view_repository import (
    PostgreSQLClaimViewRepository,
)


def test_repository_resolves_approved_postgresql_scopes() -> None:
    source = inspect.getsource(PostgreSQLClaimViewRepository.find_visible)
    assert "Poliza.id_asegurado == identity.id_asegurado" in source
    assert "AsignacionSiniestro.finalizado_en.is_(None)" in source
    assert "PrincipalRole.SUPERVISOR" in source


def test_supervisor_access_is_audited_without_token() -> None:
    source = inspect.getsource(PostgreSQLClaimViewRepository.find_visible)
    assert 'tipo_evento="consulta_sensible"' in source
    assert '"subject": principal.subject' in source
    assert "id_usuario=identity.id_usuario" in source
    assert "token" not in source.lower()
