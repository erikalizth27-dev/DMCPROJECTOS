import inspect

from siniestro_facil.persistence.fraud_repository import (
    PostgreSQLFraudAlertRepository,
)


def review_source() -> str:
    return inspect.getsource(PostgreSQLFraudAlertRepository.review)


def test_review_uses_single_transaction_and_row_lock() -> None:
    source = review_source()
    assert "with self._factory() as session, session.begin()" in source
    assert ".with_for_update()" in source
    assert "with_for_update=True" in source


def test_review_requires_linked_internal_identity() -> None:
    source = review_source()
    assert "IdentidadActor" in source
    assert "identity.id_usuario is None" in source
    assert '"ALERT-REVIEW-FORBIDDEN"' in source


def test_review_checks_optimistic_version_and_pending_state() -> None:
    source = review_source()
    assert "alert.version != command.expected_version" in source
    assert '"ALERT-VERSION-CONFLICT"' in source
    assert "AlertReviewStatus.PENDIENTE.value" in source
    assert '"ALERT-ALREADY-REVIEWED"' in source


def test_review_persists_decision_audit_and_idempotency() -> None:
    source = review_source()
    assert "alert.estado_revision = command.target.value" in source
    assert "alert.justificacion_revision = command.justification.strip()" in source
    assert "alert.version += 1" in source
    assert 'tipo_evento="alerta_fraude_revisada"' in source
    assert "SolicitudRevisionAlertaIdempotente(" in source


def test_review_recovers_idempotency_race() -> None:
    source = review_source()
    assert "except IntegrityError as exc" in source
    assert "self.find_review_request(idempotency_key)" in source
    assert '"IDEMPOTENCY-CONFLICT"' in source


def test_sensitive_access_is_audited_with_actor() -> None:
    source = inspect.getsource(
        PostgreSQLFraudAlertRepository.audit_alert_access
    )
    assert "IdentidadActor" in source
    assert "id_usuario=identity.id_usuario" in source
    assert 'tipo_evento="acceso_alerta_fraude_sensible"' in source
