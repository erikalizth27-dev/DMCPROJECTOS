from __future__ import annotations

from decimal import Decimal
from functools import lru_cache

from fastapi import APIRouter, Depends, Header, status
from pydantic import Field

from siniestro_facil.api.errors import BusinessError
from siniestro_facil.api.routes.claims import get_authenticated_principal
from siniestro_facil.api.schemas import ApiModel
from siniestro_facil.application.manage_payment import (
    AuthorizePaymentCommand,
    AuthorizePaymentService,
    InMemoryPaymentRepository,
    PaymentOperationError,
    PaymentRecord,
    PreparePaymentCommand,
    PreparePaymentService,
)
from siniestro_facil.domain.identity import AuthenticatedPrincipal
from siniestro_facil.infrastructure.payment_adapter import (
    DeterministicPaymentAdapter,
)


router = APIRouter(prefix="/api/v1/siniestros", tags=["Pagos"])


class PrepararPagoRequest(ApiModel):
    monto: Decimal = Field(gt=0)


class AutorizarPagoRequest(ApiModel):
    version: int = Field(ge=0)


class PagoResponse(ApiModel):
    id: int
    siniestro_id: int = Field(alias="siniestroId")
    monto: Decimal
    estado: str
    preparado_por: str = Field(alias="preparadoPor")
    autorizado_por: str | None = Field(alias="autorizadoPor")
    version: int
    simulado: bool
    transferencia_realizada: bool = Field(alias="transferenciaRealizada")


@lru_cache(maxsize=1)
def get_payment_repository() -> InMemoryPaymentRepository:
    # Primera entrega: se sustituye por PostgreSQL en la segunda entrega.
    return InMemoryPaymentRepository()


def get_prepare_payment_service() -> PreparePaymentService:
    return PreparePaymentService(get_payment_repository())


def get_authorize_payment_service() -> AuthorizePaymentService:
    return AuthorizePaymentService(
        get_payment_repository(),
        DeterministicPaymentAdapter(version="pilot-1"),
    )


def _response(payment: PaymentRecord) -> PagoResponse:
    return PagoResponse(
        id=payment.id,
        siniestroId=payment.claim_id,
        monto=payment.amount,
        estado=payment.status.value,
        preparadoPor=payment.preparer_subject,
        autorizadoPor=payment.authorizer_subject,
        version=payment.version,
        simulado=payment.simulated,
        transferenciaRealizada=payment.money_transferred,
    )


@router.post(
    "/{siniestro_id}/pagos",
    response_model=PagoResponse,
    status_code=status.HTTP_201_CREATED,
)
def prepare_payment(
    siniestro_id: int,
    request: PrepararPagoRequest,
    idempotency_key: str = Header(alias="Idempotency-Key"),
    principal: AuthenticatedPrincipal = Depends(get_authenticated_principal),
    service: PreparePaymentService = Depends(get_prepare_payment_service),
) -> PagoResponse:
    try:
        result = service.execute(
            PreparePaymentCommand(
                claim_id=siniestro_id,
                amount=request.monto,
            ),
            principal,
            idempotency_key=idempotency_key,
            request_payload={
                "siniestroId": siniestro_id,
                **request.model_dump(mode="json", by_alias=True),
            },
        )
    except PaymentOperationError as exc:
        raise BusinessError(exc.code, exc.message, exc.status_code) from exc
    return _response(result)


@router.post(
    "/{siniestro_id}/pagos/{pago_id}/autorizacion",
    response_model=PagoResponse,
)
def authorize_payment(
    siniestro_id: int,
    pago_id: int,
    request: AutorizarPagoRequest,
    idempotency_key: str = Header(alias="Idempotency-Key"),
    principal: AuthenticatedPrincipal = Depends(get_authenticated_principal),
    service: AuthorizePaymentService = Depends(
        get_authorize_payment_service
    ),
) -> PagoResponse:
    try:
        result = service.execute(
            AuthorizePaymentCommand(
                claim_id=siniestro_id,
                payment_id=pago_id,
                expected_version=request.version,
            ),
            principal,
            idempotency_key=idempotency_key,
            request_payload={
                "siniestroId": siniestro_id,
                "pagoId": pago_id,
                **request.model_dump(mode="json", by_alias=True),
            },
        )
    except PaymentOperationError as exc:
        raise BusinessError(exc.code, exc.message, exc.status_code) from exc
    return _response(result)
