import inspect

from siniestro_facil.persistence.fraud_repository import (
    PostgreSQLFraudAlertRepository,
)


def create_source() -> str:
    return inspect.getsource(PostgreSQLFraudAlertRepository.create)


def test_repository_uses_single_transaction_and_locks_claim() -> None:
    source = create_source()
    assert "with self._factory() as session, session.begin()" in source
    assert "with_for_update=True" in source


def test_repository_requires_linked_internal_identity() -> None:
    source = create_source()
    assert "IdentidadActor" in source
    assert "identity.id_usuario is None" in source
    assert '"FRAUD-EVALUATION-FORBIDDEN"' in source


def test_repository_requires_exact_policy_version() -> None:
    source = create_source()
    assert "policy_versions" in source
    assert "PoliticaAlerta.version.in_" in source
    assert '"FRAUD-POLICY-NOT-FOUND"' in source


def test_repository_persists_signals_alerts_and_atomic_audit() -> None:
    source = create_source()
    assert "SenalRiesgo(" in source
    assert "Alerta(" in source
    assert "EventoLineaTiempo(" in source
    assert 'tipo_evento="evaluacion_fraude_ejecutada"' in source


def test_repository_persists_idempotency_and_handles_race() -> None:
    source = create_source()
    assert "SolicitudEvaluacionFraudeIdempotente(" in source
    assert "existing.huella == fingerprint" in source
    assert "except IntegrityError as exc" in source
    assert '"IDEMPOTENCY-CONFLICT"' in source


def test_repository_reads_alert_with_versioned_policy() -> None:
    source = inspect.getsource(PostgreSQLFraudAlertRepository.get_alert)
    assert "select(Alerta, PoliticaAlerta.version)" in source
    assert "Alerta.id_siniestro == claim_id" in source
