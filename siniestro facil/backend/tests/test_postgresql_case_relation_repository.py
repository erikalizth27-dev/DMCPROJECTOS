import inspect

from siniestro_facil.persistence.case_relation_repository import (
    PostgreSQLCaseRelationRepository,
)


def create_source() -> str:
    return inspect.getsource(PostgreSQLCaseRelationRepository.create)


def test_repository_uses_single_transaction_and_locks_rows() -> None:
    source = create_source()
    assert "with self._factory() as session, session.begin()" in source
    assert "with_for_update=True" in source
    assert ".with_for_update()" in source


def test_repository_requires_linked_internal_identity() -> None:
    source = create_source()
    assert "IdentidadActor" in source
    assert "identity.id_usuario is None" in source
    assert '"CASE-RELATION-FORBIDDEN"' in source


def test_repository_verifies_all_claims_exist() -> None:
    source = create_source()
    assert "existing_claims != claim_ids" in source
    assert '"CLAIM-NOT-FOUND"' in source


def test_repository_deduplicates_pair_and_criterion() -> None:
    source = create_source()
    assert "RelacionCasos.id_siniestro_a == claim_a" in source
    assert "RelacionCasos.id_siniestro_b == claim_b" in source
    assert "RelacionCasos.criterio_relacion" in source
    assert "if relation is None:" in source


def test_repository_persists_normalized_value_without_merging() -> None:
    source = create_source()
    assert "valor_normalizado=value" in source
    assert 'estado_revision="pendiente_revision"' in source
    assert '"fusion_automatica": False' in source


def test_repository_persists_audit_and_idempotency() -> None:
    source = create_source()
    assert 'tipo_evento="relaciones_casos_detectadas"' in source
    assert "SolicitudRelacionCasosIdempotente(" in source


def test_repository_recovers_idempotency_race() -> None:
    source = create_source()
    assert "except IntegrityError as exc" in source
    assert "self.find_request(idempotency_key)" in source
    assert '"IDEMPOTENCY-CONFLICT"' in source
