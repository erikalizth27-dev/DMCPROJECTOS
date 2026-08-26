from __future__ import annotations

from datetime import date
from decimal import Decimal
from functools import lru_cache

from fastapi import APIRouter, Depends, Header, status

from siniestro_facil.api.errors import BusinessError
from siniestro_facil.api.schemas import CrearSiniestroRequest, SiniestroResponse
from siniestro_facil.application.register_claim import (
    ClaimRegistrationError,
    InMemoryClaimRepository,
    RegisterClaimCommand,
    RegisterClaimService,
)
from siniestro_facil.infrastructure.policy_adapter import (
    InMemoryPolicyAdapter,
    PolicySnapshot,
)


router = APIRouter(prefix="/api/v1/siniestros", tags=["Siniestros"])


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
            )
        ]
    )
    return RegisterClaimService(policies, InMemoryClaimRepository())


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
