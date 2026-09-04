from datetime import datetime, timedelta, timezone

import pytest

from siniestro_facil.domain.operational_metrics import (
    IndicatorAvailability,
    IndicatorName,
    elapsed_indicator,
    unavailable_indicator,
)


def test_elapsed_indicator_uses_existing_events() -> None:
    start = datetime(2026, 9, 3, 10, tzinfo=timezone.utc)
    result = elapsed_indicator(
        name=IndicatorName.TIEMPO_PRIMERA_ASISTENCIA,
        started_at=start,
        completed_at=start + timedelta(minutes=7),
        sources=("siniestro.creado_en", "asistencia.creado_en"),
        period_start=start,
        period_end=start + timedelta(days=1),
    )
    assert result.availability is IndicatorAvailability.DISPONIBLE
    assert result.value_seconds == 420
    assert result.sources == (
        "siniestro.creado_en",
        "asistencia.creado_en",
    )


def test_missing_event_is_not_reported_as_zero() -> None:
    result = elapsed_indicator(
        name=IndicatorName.TIEMPO_HASTA_DECISION,
        started_at=datetime.now(timezone.utc),
        completed_at=None,
        sources=("siniestro.creado_en", "evento_linea_tiempo.fecha"),
    )
    assert result.availability is IndicatorAvailability.NO_DISPONIBLE
    assert result.value_seconds is None
    assert result.reason


def test_invalid_event_order_is_rejected() -> None:
    end = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="preceder"):
        elapsed_indicator(
            name=IndicatorName.TIEMPO_HASTA_DECISION,
            started_at=end,
            completed_at=end - timedelta(seconds=1),
            sources=(),
        )


@pytest.mark.parametrize(
    "name",
    [
        IndicatorName.SATISFACCION_CLIENTE,
        IndicatorName.COSTO_OPERATIVO,
        IndicatorName.PERDIDAS_EVITADAS_FRAUDE,
    ],
)
def test_indicator_without_approved_source_is_unavailable(name) -> None:
    result = unavailable_indicator(
        name,
        reason="Fuente de datos no definida",
    )
    assert result.availability is IndicatorAvailability.NO_DISPONIBLE
    assert result.value_seconds is None
    assert result.sources == ()


def test_unavailable_indicator_requires_explanation() -> None:
    with pytest.raises(ValueError, match="obligatoria"):
        unavailable_indicator(
            IndicatorName.SATISFACCION_CLIENTE,
            reason=" ",
        )
