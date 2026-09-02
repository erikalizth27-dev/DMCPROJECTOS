from __future__ import annotations

from datetime import datetime
from functools import lru_cache

from fastapi import APIRouter, Depends, Header, status
from pydantic import Field

from siniestro_facil.api.errors import BusinessError
from siniestro_facil.api.routes.claims import get_authenticated_principal
from siniestro_facil.api.schemas import ApiModel
from siniestro_facil.application.assistance_contracts import AssistanceRecord
from siniestro_facil.application.manage_assistance import (
    AssistanceManagementError,
    ReassignAssistanceCommand,
    ReassignAssistanceService,
    RegisterProviderReplyCommand,
    RegisterProviderReplyService,
)
from siniestro_facil.application.request_assistance import (
    AssistanceRequestError,
    GetAssistanceService,
    RequestAssistanceCommand,
    RequestAssistanceService,
)
from siniestro_facil.config import Settings
from siniestro_facil.db import create_database_engine
from siniestro_facil.domain.assistance import ProviderResult
from siniestro_facil.domain.identity import AuthenticatedPrincipal
from siniestro_facil.infrastructure.provider_adapter import (
    SimulatedProviderAdapter,
)
from siniestro_facil.persistence.assistance_repository import (
    PostgreSQLAssistanceRepository,
)
from siniestro_facil.persistence.session import create_session_factory


router = APIRouter(prefix="/api/v1/siniestros", tags=["Asistencia"])


class SolicitarAsistenciaApiRequest(ApiModel):
    proveedor_id: int = Field(alias="proveedorId", gt=0)
    tipo_asistencia: str = Field(
        alias="tipoAsistencia",
        min_length=1,
        max_length=50,
    )
    motivo: str = Field(min_length=1, max_length=500)


class RegistrarRespuestaProveedorRequest(ApiModel):
    resultado: ProviderResult
    intento_esperado: int = Field(alias="intentoEsperado", gt=0)
    referencia_externa: str | None = Field(
        default=None,
        alias="referenciaExterna",
        max_length=120,
    )


class ReasignarAsistenciaRequest(ApiModel):
    nuevo_proveedor_id: int = Field(alias="nuevoProveedorId", gt=0)
    intento_esperado: int = Field(alias="intentoEsperado", gt=0)
    motivo: str = Field(min_length=1, max_length=500)


class AsistenciaResponse(ApiModel):
    id: int
    siniestro_id: int = Field(alias="siniestroId")
    proveedor_id: int = Field(alias="proveedorId")
    tipo_asistencia: str = Field(alias="tipoAsistencia")
    estado: str
    numero_intento: int = Field(alias="numeroIntento")
    creado_en: datetime = Field(alias="creadoEn")
    actualizado_en: datetime = Field(alias="actualizadoEn")


@lru_cache(maxsize=1)
def get_assistance_repository() -> PostgreSQLAssistanceRepository:
    settings = Settings.from_environment()
    if not settings.database_url:
        raise BusinessError(
            "SERVICE-NOT-READY",
            "Servicio de asistencia no disponible",
            503,
        )
    engine = create_database_engine(settings)
    return PostgreSQLAssistanceRepository(
        create_session_factory(engine)
    )


@lru_cache(maxsize=1)
def get_request_assistance_service() -> RequestAssistanceService:
    return RequestAssistanceService(
        get_assistance_repository(),
        SimulatedProviderAdapter(),
    )


@lru_cache(maxsize=1)
def get_get_assistance_service() -> GetAssistanceService:
    return GetAssistanceService(get_assistance_repository())


@lru_cache(maxsize=1)
def get_register_provider_reply_service() -> RegisterProviderReplyService:
    return RegisterProviderReplyService(get_assistance_repository())


@lru_cache(maxsize=1)
def get_reassign_assistance_service() -> ReassignAssistanceService:
    return ReassignAssistanceService(get_assistance_repository())


def _response(result: AssistanceRecord) -> AsistenciaResponse:
    return AsistenciaResponse(
        id=result.id,
        siniestroId=result.claim_id,
        proveedorId=result.provider_id,
        tipoAsistencia=result.assistance_type,
        estado=result.status.value,
        numeroIntento=result.attempt,
        creadoEn=result.created_at,
        actualizadoEn=result.updated_at,
    )


@router.post(
    "/{siniestro_id}/asistencias",
    response_model=AsistenciaResponse,
    status_code=status.HTTP_201_CREATED,
)
def request_assistance(
    siniestro_id: int,
    request: SolicitarAsistenciaApiRequest,
    idempotency_key: str = Header(alias="Idempotency-Key"),
    principal: AuthenticatedPrincipal = Depends(get_authenticated_principal),
    service: RequestAssistanceService = Depends(
        get_request_assistance_service
    ),
) -> AsistenciaResponse:
    try:
        result = service.execute(
            RequestAssistanceCommand(
                claim_id=siniestro_id,
                provider_id=request.proveedor_id,
                assistance_type=request.tipo_asistencia,
                reason=request.motivo,
            ),
            principal,
            idempotency_key=idempotency_key,
            request_payload=request.model_dump(mode="json", by_alias=True),
        )
    except AssistanceRequestError as exc:
        raise BusinessError(
            exc.code,
            exc.message,
            exc.status_code,
        ) from exc
    return _response(result)


@router.get(
    "/{siniestro_id}/asistencias/{asistencia_id}",
    response_model=AsistenciaResponse,
)
def get_assistance(
    siniestro_id: int,
    asistencia_id: int,
    principal: AuthenticatedPrincipal = Depends(get_authenticated_principal),
    service: GetAssistanceService = Depends(get_get_assistance_service),
) -> AsistenciaResponse:
    try:
        result = service.execute(
            siniestro_id,
            asistencia_id,
            principal,
        )
    except AssistanceRequestError as exc:
        raise BusinessError(
            exc.code,
            exc.message,
            exc.status_code,
        ) from exc
    return _response(result)


@router.post(
    "/{siniestro_id}/asistencias/{asistencia_id}/respuesta",
    response_model=AsistenciaResponse,
)
def register_provider_reply(
    siniestro_id: int,
    asistencia_id: int,
    request: RegistrarRespuestaProveedorRequest,
    principal: AuthenticatedPrincipal = Depends(get_authenticated_principal),
    service: RegisterProviderReplyService = Depends(
        get_register_provider_reply_service
    ),
) -> AsistenciaResponse:
    try:
        result = service.execute(
            RegisterProviderReplyCommand(
                claim_id=siniestro_id,
                assistance_id=asistencia_id,
                result=request.resultado,
                expected_attempt=request.intento_esperado,
                external_reference=request.referencia_externa,
            ),
            principal,
        )
    except AssistanceManagementError as exc:
        raise BusinessError(
            exc.code,
            exc.message,
            exc.status_code,
        ) from exc
    return _response(result)


@router.post(
    "/{siniestro_id}/asistencias/{asistencia_id}/reasignacion",
    response_model=AsistenciaResponse,
    status_code=status.HTTP_201_CREATED,
)
def reassign_assistance(
    siniestro_id: int,
    asistencia_id: int,
    request: ReasignarAsistenciaRequest,
    principal: AuthenticatedPrincipal = Depends(get_authenticated_principal),
    service: ReassignAssistanceService = Depends(
        get_reassign_assistance_service
    ),
) -> AsistenciaResponse:
    try:
        result = service.execute(
            ReassignAssistanceCommand(
                claim_id=siniestro_id,
                assistance_id=asistencia_id,
                new_provider_id=request.nuevo_proveedor_id,
                expected_attempt=request.intento_esperado,
                reason=request.motivo,
            ),
            principal,
        )
    except AssistanceManagementError as exc:
        raise BusinessError(
            exc.code,
            exc.message,
            exc.status_code,
        ) from exc
    return _response(result)
