from __future__ import annotations

from datetime import date, datetime
from functools import lru_cache

from fastapi import APIRouter, Depends, status
from pydantic import Field

from siniestro_facil.api.errors import BusinessError
from siniestro_facil.api.routes.claims import get_authenticated_principal
from siniestro_facil.api.schemas import ApiModel
from siniestro_facil.application.submit_budget import (
    BudgetSubmissionError,
    GetBudgetService,
    InMemoryBudgetSubmissionRepository,
    SubmitBudgetCommand,
    SubmitBudgetService,
    SubmittedBudget,
)
from siniestro_facil.application.schedule_inspection import (
    GetInspectionService,
    InMemoryInspectionSchedulingRepository,
    InspectionSchedulingError,
    InspectionSchedulingRepository,
    ScheduleInspectionCommand,
    ScheduleInspectionService,
    ScheduledInspection,
)
from siniestro_facil.config import Settings
from siniestro_facil.db import create_database_engine
from siniestro_facil.domain.identity import AuthenticatedPrincipal
from siniestro_facil.persistence.inspection_budget_repository import (
    PostgreSQLInspectionSchedulingRepository,
)
from siniestro_facil.persistence.session import create_session_factory


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

class PresentarPresupuestoRequest(ApiModel):
    diagnostico: str = Field(min_length=1, max_length=4000)
    fecha_presentacion: date = Field(alias="fechaPresentacion")
    version: int = Field(ge=0)


class PresupuestoResponse(ApiModel):
    id: int
    siniestro_id: int = Field(alias="siniestroId")
    inspeccion_id: int = Field(alias="inspeccionId")
    proveedor_id: int = Field(alias="proveedorId")
    diagnostico: str
    vigencia_desde: date = Field(alias="vigenciaDesde")
    vigencia_hasta: date = Field(alias="vigenciaHasta")
    estado: str
    estado_actual: str = Field(alias="estadoActual")
    version: int


@lru_cache(maxsize=1)
def get_inspection_repository() -> InspectionSchedulingRepository:
    settings = Settings.from_environment()
    if not settings.database_url:
        return InMemoryInspectionSchedulingRepository()
    engine = create_database_engine(settings)
    return PostgreSQLInspectionSchedulingRepository(
        create_session_factory(engine)
    )


def get_schedule_inspection_service() -> ScheduleInspectionService:
    return ScheduleInspectionService(get_inspection_repository())


def get_get_inspection_service() -> GetInspectionService:
    return GetInspectionService(get_inspection_repository())


@lru_cache(maxsize=1)
def get_budget_repository() -> InMemoryBudgetSubmissionRepository:
    # Primera entrega; PostgreSQL se incorpora antes de cerrar S4-BE-02.
    return InMemoryBudgetSubmissionRepository()


def get_submit_budget_service() -> SubmitBudgetService:
    return SubmitBudgetService(get_budget_repository())


def get_get_budget_service() -> GetBudgetService:
    return GetBudgetService(get_budget_repository())


def _response(result: ScheduledInspection) -> InspeccionResponse:
    return InspeccionResponse(
        id=result.id,
        siniestroId=result.claim_id,
        fechaProgramada=result.scheduled_at,
        estadoActual=result.current_state.value,
        version=result.version,
    )


def _budget_response(result: SubmittedBudget) -> PresupuestoResponse:
    return PresupuestoResponse(
        id=result.id,
        siniestroId=result.claim_id,
        inspeccionId=result.inspection_id,
        proveedorId=result.provider_id,
        diagnostico=result.diagnosis,
        vigenciaDesde=result.valid_from,
        vigenciaHasta=result.valid_until,
        estado=result.status.value,
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


@router.post(
    "/{siniestro_id}/inspecciones/{inspeccion_id}/presupuestos",
    response_model=PresupuestoResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_budget(
    siniestro_id: int,
    inspeccion_id: int,
    request: PresentarPresupuestoRequest,
    principal: AuthenticatedPrincipal = Depends(get_authenticated_principal),
    service: SubmitBudgetService = Depends(get_submit_budget_service),
) -> PresupuestoResponse:
    try:
        result = service.execute(
            SubmitBudgetCommand(
                claim_id=siniestro_id,
                inspection_id=inspeccion_id,
                diagnosis=request.diagnostico,
                presented_on=request.fecha_presentacion,
                expected_version=request.version,
            ),
            principal,
        )
    except BudgetSubmissionError as exc:
        raise BusinessError(exc.code, exc.message, exc.status_code) from exc
    return _budget_response(result)


@router.get(
    "/{siniestro_id}/presupuestos/{presupuesto_id}",
    response_model=PresupuestoResponse,
)
def get_budget(
    siniestro_id: int,
    presupuesto_id: int,
    principal: AuthenticatedPrincipal = Depends(get_authenticated_principal),
    service: GetBudgetService = Depends(get_get_budget_service),
) -> PresupuestoResponse:
    try:
        result = service.execute(siniestro_id, presupuesto_id, principal)
    except BudgetSubmissionError as exc:
        raise BusinessError(exc.code, exc.message, exc.status_code) from exc
    return _budget_response(result)
