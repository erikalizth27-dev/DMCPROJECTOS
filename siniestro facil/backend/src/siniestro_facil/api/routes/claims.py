from __future__ import annotations

from datetime import date
from decimal import Decimal
from functools import lru_cache

from fastapi import APIRouter, Depends, Header, status

from siniestro_facil.api.errors import BusinessError
from siniestro_facil.api.schemas import (
    CambiarEstadoRequest,
    CambiarEstadoResponse,
    EvidenciaResponse,
    CrearSiniestroRequest,
    RegistrarEvidenciaRequest,
    SiniestroResponse,
    VerificarCoberturaRequest,
    VerificarCoberturaResponse,
)
from siniestro_facil.application.change_claim_state import (
    ChangeClaimStateCommand,
    ChangeClaimStateService,
    ClaimStateChangeError,
)
from siniestro_facil.application.get_claim_view import (
    ClaimNotVisible,
    GetClaimViewService,
)
from siniestro_facil.application.verify_coverage import (
    CoverageVerificationError,
    VerifyCoverageCommand,
    VerifyCoverageService,
)
from siniestro_facil.application.register_evidence import (
    EvidenceRegistrationError,
    RegisterEvidenceCommand,
    RegisterEvidenceService,
)
from siniestro_facil.application.register_claim import (
    ClaimRegistrationError,
    InMemoryClaimRepository,
    RegisterClaimCommand,
    RegisterClaimService,
)
from siniestro_facil.config import Settings
from siniestro_facil.db import create_database_engine
from siniestro_facil.domain.enums import EstadoSiniestro
from siniestro_facil.domain.identity import AuthenticatedPrincipal
from siniestro_facil.infrastructure.policy_adapter import (
    InMemoryPolicyAdapter,
    PolicySnapshot,
)
from siniestro_facil.persistence.claim_repository import PostgreSQLClaimRepository
from siniestro_facil.persistence.claim_state_repository import (
    PostgreSQLClaimStateRepository,
)
from siniestro_facil.persistence.evidence_repository import (
    PostgreSQLEvidenceRepository,
)
from siniestro_facil.persistence.coverage_repository import (
    PostgreSQLCoverageRepository,
)
from siniestro_facil.persistence.claim_view_repository import (
    PostgreSQLClaimViewRepository,
)
from siniestro_facil.persistence.session import create_session_factory


router = APIRouter(prefix="/api/v1/siniestros", tags=["Siniestros"])


def get_authenticated_principal() -> AuthenticatedPrincipal:
    # Denegación por defecto hasta que el adaptador criptográfico entregue
    # claims ya verificados. Las pruebas sustituyen esta dependencia.
    raise BusinessError(
        "AUTHENTICATION-REQUIRED",
        "Autenticación requerida",
        401,
    )


@lru_cache(maxsize=1)
def get_register_claim_service() -> RegisterClaimService:
    policies = InMemoryPolicyAdapter(
        [
            PolicySnapshot(
                numero_poliza="POL-SYN-001",
                numero_documento="DOC-SYN-001",
                placa="SYN0001",
                vigente_desde=date(2026, 1, 1),
                vigente_hasta=date(2026, 12, 31),
                deducible=Decimal("500.00"),
            ),
            PolicySnapshot(
                numero_poliza="SYN-20260820-POL-0001",
                numero_documento="SYN-20260820-0001",
                placa="SYN0001",
                vigente_desde=date(2026, 1, 1),
                vigente_hasta=date(2026, 12, 31),
                deducible=Decimal("525.00"),
            ),
        ]
    )
    settings = Settings.from_environment()
    if settings.database_url:
        engine = create_database_engine(settings)
        repository = PostgreSQLClaimRepository(create_session_factory(engine))
    else:
        repository = InMemoryClaimRepository()
    return RegisterClaimService(policies, repository)


@lru_cache(maxsize=1)
def get_claim_view_service() -> GetClaimViewService:
    settings = Settings.from_environment()
    if not settings.database_url:
        raise BusinessError(
            "SERVICE-NOT-READY",
            "Servicio de consulta no disponible",
            503,
        )
    engine = create_database_engine(settings)
    repository = PostgreSQLClaimViewRepository(create_session_factory(engine))
    return GetClaimViewService(repository)


@lru_cache(maxsize=1)
def get_change_claim_state_service() -> ChangeClaimStateService:
    settings = Settings.from_environment()
    if not settings.database_url:
        raise BusinessError(
            "SERVICE-NOT-READY",
            "Servicio de transición no disponible",
            503,
        )
    engine = create_database_engine(settings)
    repository = PostgreSQLClaimStateRepository(create_session_factory(engine))
    return ChangeClaimStateService(repository)


@lru_cache(maxsize=1)
def get_verify_coverage_service() -> VerifyCoverageService:
    settings = Settings.from_environment()
    if not settings.database_url:
        raise BusinessError(
            "SERVICE-NOT-READY",
            "Servicio de cobertura no disponible",
            503,
        )
    policies = InMemoryPolicyAdapter(
        [
            PolicySnapshot(
                numero_poliza="POL-SYN-001",
                numero_documento="DOC-SYN-001",
                placa="SYN0001",
                vigente_desde=date(2026, 1, 1),
                vigente_hasta=date(2026, 12, 31),
                deducible=Decimal("500.00"),
            ),
            PolicySnapshot(
                numero_poliza="SYN-20260820-POL-0001",
                numero_documento="SYN-20260820-0001",
                placa="SYN0001",
                vigente_desde=date(2026, 1, 1),
                vigente_hasta=date(2026, 12, 31),
                deducible=Decimal("525.00"),
            ),
        ]
    )
    engine = create_database_engine(settings)
    repository = PostgreSQLCoverageRepository(create_session_factory(engine))
    return VerifyCoverageService(policies, repository)


@lru_cache(maxsize=1)
def get_register_evidence_service() -> RegisterEvidenceService:
    settings = Settings.from_environment()
    if not settings.database_url:
        raise BusinessError(
            "SERVICE-NOT-READY",
            "Servicio de evidencia no disponible",
            503,
        )
    engine = create_database_engine(settings)
    repository = PostgreSQLEvidenceRepository(
        create_session_factory(engine)
    )
    return RegisterEvidenceService(repository)


@router.post("", response_model=SiniestroResponse, status_code=status.HTTP_201_CREATED)
def create_claim(
    request: CrearSiniestroRequest,
    idempotency_key: str = Header(alias="Idempotency-Key"),
    service: RegisterClaimService = Depends(get_register_claim_service),
) -> SiniestroResponse:
    command = RegisterClaimCommand(
        numero_poliza=request.numero_poliza,
        numero_documento=request.numero_documento,
        placa=request.placa,
        fecha_evento=request.fecha_evento,
        ubicacion_evento=request.ubicacion_evento,
        tipo_evento=request.tipo_evento,
        medio_contacto=request.medio_contacto,
    )
    try:
        result = service.execute(
            command,
            idempotency_key=idempotency_key,
            request_payload=request.model_dump(mode="json", by_alias=True),
        )
    except ClaimRegistrationError as exc:
        raise BusinessError(exc.code, exc.message, exc.status_code) from exc

    return SiniestroResponse(
        id=result.id,
        estadoActual=result.estado_actual,
        fechaEvento=result.fecha_evento,
        tipoEvento=result.tipo_evento,
        siguientePaso=result.siguiente_paso,
    )


@router.post(
    "/{siniestro_id}/evidencias",
    response_model=EvidenciaResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_claim_evidence(
    siniestro_id: int,
    request: RegistrarEvidenciaRequest,
    idempotency_key: str = Header(alias="Idempotency-Key"),
    principal: AuthenticatedPrincipal = Depends(get_authenticated_principal),
    service: RegisterEvidenceService = Depends(
        get_register_evidence_service
    ),
) -> EvidenciaResponse:
    command = RegisterEvidenceCommand(
        claim_id=siniestro_id,
        evidence_type=request.tipo_evidencia,
        original_uri=request.contenido_original_uri,
        sha256_hex=request.hash,
        captured_at=request.fecha_captura,
        source=request.fuente,
        derived_from_id=request.version_derivada_de,
        metadata=request.metadatos,
    )
    try:
        result = service.execute(
            command,
            principal,
            idempotency_key=idempotency_key,
            request_payload=request.model_dump(
                mode="json",
                by_alias=True,
            ),
        )
    except EvidenceRegistrationError as exc:
        raise BusinessError(
            exc.code,
            exc.message,
            exc.status_code,
        ) from exc

    return EvidenciaResponse(
        id=result.id,
        siniestroId=result.claim_id,
        tipoEvidencia=result.evidence_type,
        contenidoOriginalUri=result.original_uri,
        hash=result.sha256_hex,
        fechaRecepcion=result.received_at,
        versionDerivadaDe=result.derived_from_id,
    )


@router.post(
    "/{siniestro_id}/cobertura/verificacion",
    response_model=VerificarCoberturaResponse,
)
def verify_claim_coverage(
    siniestro_id: int,
    request: VerificarCoberturaRequest,
    principal: AuthenticatedPrincipal = Depends(get_authenticated_principal),
    service: VerifyCoverageService = Depends(get_verify_coverage_service),
) -> VerificarCoberturaResponse:
    try:
        result = service.execute(
            VerifyCoverageCommand(
                claim_id=siniestro_id,
                expected_version=request.version,
            ),
            principal,
        )
    except CoverageVerificationError as exc:
        raise BusinessError(exc.code, exc.message, exc.status_code) from exc

    return VerificarCoberturaResponse(
        siniestroId=result.claim_id,
        coberturaActiva=result.active,
        deducible=result.deductible,
        estadoValidacion=result.validation_status,
        estadoActual=result.current_state,
        version=result.version,
        requiereRevisionHumana=result.human_review_required,
    )


@router.post(
    "/{siniestro_id}/estado",
    response_model=CambiarEstadoResponse,
)
def change_claim_state(
    siniestro_id: int,
    request: CambiarEstadoRequest,
    principal: AuthenticatedPrincipal = Depends(get_authenticated_principal),
    service: ChangeClaimStateService = Depends(get_change_claim_state_service),
) -> CambiarEstadoResponse:
    command = ChangeClaimStateCommand(
        claim_id=siniestro_id,
        target_state=request.estado_destino,
        reason=request.motivo,
        expected_version=request.version,
        human_confirmation=request.estado_destino is EstadoSiniestro.RECHAZADO,
    )
    try:
        result = service.execute(command, principal)
    except ClaimStateChangeError as exc:
        raise BusinessError(exc.code, exc.message, exc.status_code) from exc

    return CambiarEstadoResponse(
        id=result.id,
        estadoActual=result.current_state,
        version=result.version,
    )


@router.get("/{siniestro_id}", response_model=SiniestroResponse)
def get_claim(
    siniestro_id: int,
    principal: AuthenticatedPrincipal = Depends(get_authenticated_principal),
    service: GetClaimViewService = Depends(get_claim_view_service),
) -> SiniestroResponse:
    try:
        result = service.execute(siniestro_id, principal)
    except ClaimNotVisible as exc:
        raise BusinessError(
            "CLAIM-NOT-FOUND",
            "Siniestro no encontrado",
            404,
        ) from exc

    return SiniestroResponse(
        id=result.id,
        estadoActual=result.estado_actual,
        fechaEvento=result.fecha_evento,
        tipoEvento=result.tipo_evento,
        siguientePaso=result.siguiente_paso,
    )
