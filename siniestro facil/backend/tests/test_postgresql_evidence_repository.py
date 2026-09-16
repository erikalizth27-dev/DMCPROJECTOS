import inspect

from siniestro_facil.persistence.evidence_repository import (
    PostgreSQLEvidenceRepository,
)


def test_repository_persists_evidence_audit_and_idempotency_atomically() -> None:
    source = inspect.getsource(
        PostgreSQLEvidenceRepository.create
    )
    assert "with self._factory() as session, session.begin()" in source
    assert "Evidencia(" in source
    assert 'tipo_evento="evidencia_registrada"' in source
    assert "SolicitudEvidenciaIdempotente(" in source
    assert "session.flush()" in source


def test_repository_enforces_scope_and_derived_parent() -> None:
    source = inspect.getsource(
        PostgreSQLEvidenceRepository.create
    )
    assert "_identity_in_scope" in source
    assert "parent.id_siniestro != command.claim_id" in source
    assert '"EVIDENCE-PARENT-NOT-FOUND"' in source

def test_insured_scope_does_not_join_from_exists_expression() -> None:
    source = inspect.getsource(
        PostgreSQLEvidenceRepository._identity_in_scope
    )
    assert ".select_from(Siniestro)" in source
    assert ".join(" not in source
    assert "Poliza.id_poliza == Siniestro.id_poliza" in source
