from __future__ import annotations

from datetime import datetime
from functools import lru_cache

from fastapi import APIRouter, Depends, Query

from siniestro_facil.api.errors import BusinessError
from siniestro_facil.api.routes.claims import get_authenticated_principal
from siniestro_facil.application.get_operational_metrics import (
    GetOperationalMetricsService,
    OperationalMetricsError,
)
from siniestro_facil.domain.identity import AuthenticatedPrincipal


router = APIRouter(prefix="/api/v1/indicadores", tags=["Indicadores"])


@lru_cache(maxsize=1)
def get_operational_metrics_service() -> GetOperationalMetricsService:
    # La segunda entrega conectará las fuentes PostgreSQL aprobadas.
    raise BusinessError(
        "SERVICE-NOT-READY",
        "Servicio de indicadores no disponible",
        503,
    )


@router.get("/operativos")
def get_operational_metrics(
    desde: datetime = Query(),
    hasta: datetime = Query(),
    principal: AuthenticatedPrincipal = Depends(get_authenticated_principal),
    service: GetOperationalMetricsService = Depends(
        get_operational_metrics_service
    ),
) -> dict[str, object]:
    try:
        result = service.execute(
            period_start=desde,
            period_end=hasta,
            principal=principal,
        )
    except OperationalMetricsError as exc:
        raise BusinessError(exc.code, exc.message, exc.status_code) from exc

    return {
        "periodo": {
            "desde": result.period_start,
            "hasta": result.period_end,
        },
        "indicadores": [
            {
                "nombre": indicator.name.value,
                "disponibilidad": indicator.availability.value,
                "valorSegundos": indicator.value_seconds,
                "fuentes": list(indicator.sources),
                "razon": indicator.reason,
            }
            for indicator in result.indicators
        ],
    }
