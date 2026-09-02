from __future__ import annotations

from datetime import datetime
from functools import lru_cache

from fastapi import APIRouter, Depends, status
from pydantic import Field

from siniestro_facil.api.errors import BusinessError
from siniestro_facil.api.routes.claims import get_authenticated_principal
from siniestro_facil.api.schemas import ApiModel
from siniestro_facil.application.schedule_inspection import (
    GetInspectionService,
    InMemoryInspectionSchedulingRepository,
    InspectionSchedulingError,
    ScheduleInspectionCommand,
    ScheduleInspectionService,
    ScheduledInspection,
)
from siniestro_facil.domain.identity import AuthenticatedPrincipal


router = APIRouter(prefix="/api/v1/siniestros", tags=["Inspecciones"])


class ProgramarInspeccionRequest(ApiModel):
    fecha_programada: datetime = Field(alias="fechaProgramada")
    version: int = Field(ge=0)
    motivo: str = Field(min_length=1, max_length=500)


class InspeccionResponse(ApiModel):
    id: int
    siniestro_id: int = Field(alias="siniestroId")
    fecha_programada: datetime = Field(alias="fechaProgramada")
    estado_actual: str = Field(alias="estadoActual")
    version: int


@lru_cache(maxsize=1)
def get_inspection_repository() -> InMemoryInspectionSchedulingRepository:
    # Primera entrega: se sustituirá por PostgreSQL antes de cerrar S4-BE-01.
    return InMemoryInspectionSchedulingRepository()


def get_schedule_inspection_service() -> ScheduleInspectionService:
    return ScheduleInspectionService(get_inspection_repository())


def get_get_inspection_service() -> GetInspectionService:
    return GetInspectionService(get_inspection_repository())


def _response(result: ScheduledInspection) -> InspeccionResponse:
    return InspeccionResponse(
        id=result.id,
        siniestroId=result.claim_id,
        fechaProgramada=result.scheduled_at,
        estadoActual=result.current_state.value,
        version=result.version,
    )


@router.post(
    "/{siniestro_id}/inspecciones",
    response_model=InspeccionResponse,
    status_code=status.HTTP_201_CREATED,
)
def schedule_inspection(
    siniestro_id: int,
    request: ProgramarInspeccionRequest,
    principal: AuthenticatedPrincipal = Depends(get_authenticated_principal),
    service: ScheduleInspectionService = Depends(
        get_schedule_inspection_service
    ),
) -> InspeccionResponse:
    try:
        result = service.execute(
            ScheduleInspectionCommand(
                claim_id=siniestro_id,
                scheduled_at=request.fecha_programada,
                expected_version=request.version,
                reason=request.motivo,
            ),
            principal,
        )
    except InspectionSchedulingError as exc:
        raise BusinessError(
            exc.code,
            exc.message,
            exc.status_code,
        ) from exc
    return _response(result)


@router.get(
    "/{siniestro_id}/inspecciones/{inspeccion_id}",
    response_model=InspeccionResponse,
)
def get_inspection(
    siniestro_id: int,
    inspeccion_id: int,
    principal: AuthenticatedPrincipal = Depends(get_authenticated_principal),
    service: GetInspectionService = Depends(get_get_inspection_service),
) -> InspeccionResponse:
    try:
        result = service.execute(
            siniestro_id,
            inspeccion_id,
            principal,
        )
    except InspectionSchedulingError as exc:
        raise BusinessError(
            exc.code,
            exc.message,
            exc.status_code,
        ) from exc
    return _response(result)
