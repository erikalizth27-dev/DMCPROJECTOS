import inspect

from siniestro_facil.persistence.operational_metrics_repository import (
    PostgreSQLOperationalMetricsRepository,
    TRACEABLE_DECISION_EVENTS,
)


def source() -> str:
    return inspect.getsource(
        PostgreSQLOperationalMetricsRepository.load_facts
    )


def test_requires_persisted_supervisor_identity() -> None:
    validation = inspect.getsource(
        PostgreSQLOperationalMetricsRepository._validate_supervisor
    )
    assert "IdentidadActor" in validation
    assert "UsuarioInterno" in validation
    assert "PrincipalRole.SUPERVISOR" in validation
    assert '"OPERATIONAL-METRICS-FORBIDDEN"' in validation


def test_selects_a_traceable_source_case_within_period() -> None:
    text = source()
    assert "Siniestro.creado_en >= period_start" in text
    assert "Siniestro.creado_en <= period_end" in text
    assert ".order_by(" in text
    assert ".limit(1)" in text


def test_first_assistance_is_correlated_to_source_case() -> None:
    text = source()
    assert "Asistencia.id_siniestro == claim.id_siniestro" in text
    assert "func.min(Asistencia.creado_en)" in text


def test_decision_uses_only_traceable_event_types() -> None:
    text = source()
    assert "TRACEABLE_DECISION_EVENTS" in text
    assert "func.min(EventoLineaTiempo.fecha)" in text
    assert TRACEABLE_DECISION_EVENTS == (
        "decision_presupuesto_registrada",
        "pago_autorizado",
    )


def test_missing_case_returns_unavailable_facts() -> None:
    text = source()
    assert "if claim is None" in text
    assert "OperationalMetricFacts(None, None, None, None)" in text


def test_result_identifies_source_case() -> None:
    assert "source_claim_id=claim.id_siniestro" in source()
