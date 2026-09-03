from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import AuthenticatedPrincipal
from siniestro_facil.domain.operational_metrics import (
    IndicatorName,
    IndicatorResult,
    elapsed_indicator,
    unavailable_indicator,
)


class OperationalMetricsError(RuntimeError):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


@dataclass(frozen=True, slots=True)
class OperationalMetricFacts:
    claim_created_at: datetime | None
    first_assistance_at: datetime | None
    first_decision_at: datetime | None


@dataclass(frozen=True, slots=True)
class OperationalMetricsResult:
    period_start: datetime
    period_end: datetime
    indicators: tuple[IndicatorResult, ...]


class OperationalMetricsRepository(Protocol):
    def load_facts(
        self,
        *,
        period_start: datetime,
        period_end: datetime,
    ) -> OperationalMetricFacts: ...


class GetOperationalMetricsService:
    def __init__(self, repository: OperationalMetricsRepository) -> None:
        self._repository = repository

    def execute(
        self,
        *,
        period_start: datetime,
        period_end: datetime,
        principal: AuthenticatedPrincipal,
    ) -> OperationalMetricsResult:
        if principal.role is not PrincipalRole.SUPERVISOR:
            raise OperationalMetricsError(
                "OPERATIONAL-METRICS-FORBIDDEN",
                "Solo el supervisor puede consultar indicadores",
                403,
            )
        if period_start.tzinfo is None or period_end.tzinfo is None:
            raise OperationalMetricsError(
                "OPERATIONAL-METRICS-INVALID",
                "El período debe incluir zona horaria",
                422,
            )
        if period_end < period_start:
            raise OperationalMetricsError(
                "OPERATIONAL-METRICS-INVALID",
                "El fin del período no puede preceder al inicio",
                422,
            )

        facts = self._repository.load_facts(
            period_start=period_start,
            period_end=period_end,
        )
        indicators = (
            elapsed_indicator(
                name=IndicatorName.TIEMPO_PRIMERA_ASISTENCIA,
                started_at=facts.claim_created_at,
                completed_at=facts.first_assistance_at,
                sources=("siniestro.creado_en", "asistencia.creado_en"),
                period_start=period_start,
                period_end=period_end,
            ),
            elapsed_indicator(
                name=IndicatorName.TIEMPO_HASTA_DECISION,
                started_at=facts.claim_created_at,
                completed_at=facts.first_decision_at,
                sources=(
                    "siniestro.creado_en",
                    "evento_linea_tiempo.fecha",
                ),
                period_start=period_start,
                period_end=period_end,
            ),
            unavailable_indicator(
                IndicatorName.CASOS_SIN_LLAMADAS_ADICIONALES,
                reason="Definición y fuente aprobada no disponibles",
                period_start=period_start,
                period_end=period_end,
            ),
            unavailable_indicator(
                IndicatorName.SATISFACCION_CLIENTE,
                reason="Fuente de datos no definida",
                period_start=period_start,
                period_end=period_end,
            ),
            unavailable_indicator(
                IndicatorName.COSTO_OPERATIVO,
                reason="Fuente de datos no definida",
                period_start=period_start,
                period_end=period_end,
            ),
            unavailable_indicator(
                IndicatorName.PERDIDAS_EVITADAS_FRAUDE,
                reason="Fuente de datos no definida",
                period_start=period_start,
                period_end=period_end,
            ),
        )
        return OperationalMetricsResult(
            period_start=period_start,
            period_end=period_end,
            indicators=indicators,
        )
