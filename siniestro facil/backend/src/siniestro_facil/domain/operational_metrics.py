from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Iterable


class IndicatorName(StrEnum):
    TIEMPO_PRIMERA_ASISTENCIA = "tiempo_primera_asistencia"
    TIEMPO_HASTA_DECISION = "tiempo_hasta_decision"
    CASOS_SIN_LLAMADAS_ADICIONALES = "casos_sin_llamadas_adicionales"
    SATISFACCION_CLIENTE = "satisfaccion_cliente"
    COSTO_OPERATIVO = "costo_operativo"
    PERDIDAS_EVITADAS_FRAUDE = "perdidas_evitadas_fraude"


class IndicatorAvailability(StrEnum):
    DISPONIBLE = "disponible"
    NO_DISPONIBLE = "no_disponible"


@dataclass(frozen=True, slots=True)
class IndicatorResult:
    name: IndicatorName
    availability: IndicatorAvailability
    value_seconds: int | None
    sources: tuple[str, ...]
    period_start: datetime | None
    period_end: datetime | None
    reason: str | None = None


def elapsed_indicator(
    *,
    name: IndicatorName,
    started_at: datetime | None,
    completed_at: datetime | None,
    sources: Iterable[str],
    period_start: datetime | None = None,
    period_end: datetime | None = None,
) -> IndicatorResult:
    source_tuple = tuple(sources)
    if started_at is None or completed_at is None:
        return IndicatorResult(
            name=name,
            availability=IndicatorAvailability.NO_DISPONIBLE,
            value_seconds=None,
            sources=source_tuple,
            period_start=period_start,
            period_end=period_end,
            reason="No existen todos los eventos requeridos",
        )
    if completed_at < started_at:
        raise ValueError("El evento final no puede preceder al inicial")
    return IndicatorResult(
        name=name,
        availability=IndicatorAvailability.DISPONIBLE,
        value_seconds=int((completed_at - started_at).total_seconds()),
        sources=source_tuple,
        period_start=period_start,
        period_end=period_end,
    )


def unavailable_indicator(
    name: IndicatorName,
    *,
    reason: str,
    period_start: datetime | None = None,
    period_end: datetime | None = None,
) -> IndicatorResult:
    if not reason.strip():
        raise ValueError("La razón de indisponibilidad es obligatoria")
    return IndicatorResult(
        name=name,
        availability=IndicatorAvailability.NO_DISPONIBLE,
        value_seconds=None,
        sources=(),
        period_start=period_start,
        period_end=period_end,
        reason=reason.strip(),
    )
