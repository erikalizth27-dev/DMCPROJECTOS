from __future__ import annotations

from functools import lru_cache

from fastapi import APIRouter, Depends, Header
from pydantic import Field, StrictBool

from siniestro_facil.api.errors import BusinessError
from siniestro_facil.api.routes.claims import get_authenticated_principal
from siniestro_facil.api.schemas import ApiModel
from siniestro_facil.application.evaluate_fraud import (
    AlertView,
    EvaluateFraudCommand,
    EvaluateFraudService,
    FraudEvaluationError,
    FraudEvaluationResult,
    GetFraudAlertService,
    InMemoryFraudAlertRepository,
)
from siniestro_facil.domain.fraud import AlertSeverity, RiskSignalType
from siniestro_facil.config import Settings
from siniestro_facil.db import create_database_engine
from siniestro_facil.domain.identity import AuthenticatedPrincipal
from siniestro_facil.infrastructure.fraud_adapter import (
    DeterministicFraudAdapter,
    DeterministicRule,
)
from siniestro_facil.persistence.fraud_repository import (
    PostgreSQLFraudAlertRepository,
)
from siniestro_facil.persistence.session import create_session_factory


router = APIRouter(prefix="/api/v1/siniestros", tags=["Fraude"])


class EvaluarFraudeRequest(ApiModel):
    hechos: dict[str, StrictBool] = Field(min_length=1)


class AlertaFraudeResponse(ApiModel):
    id: int
    siniestro_id: int = Field(alias="siniestroId")
    tipo: str
    severidad: str
    efecto: str
    estado_revision: str = Field(alias="estadoRevision")
    nivel_detalle: str = Field(alias="nivelDetalle")
    explicacion: str | None = None
    datos_origen: dict[str, object] | None = Field(
        default=None,
        alias="datosOrigen",
    )
    modelo_o_regla: str | None = Field(default=None, alias="modeloORegla")
    version_politica: str | None = Field(default=None, alias="versionPolitica")


class EvaluacionFraudeResponse(ApiModel):
    siniestro_id: int = Field(alias="siniestroId")
    alertas: list[AlertaFraudeResponse]


@lru_cache(maxsize=1)
def get_fraud_repository():
    settings = Settings.from_environment()
    if not settings.database_url:
        return InMemoryFraudAlertRepository()
    engine = create_database_engine(settings)
    return PostgreSQLFraudAlertRepository(create_session_factory(engine))


@lru_cache(maxsize=1)
def get_fraud_adapter() -> DeterministicFraudAdapter:
    return DeterministicFraudAdapter(
        rule_set="pilot-fraud",
        version="1",
        policy_version="pilot-1",
        rules=(
            DeterministicRule(
                fact_key="participante_repetido",
                signal_type=RiskSignalType.PARTICIPANTE_REPETIDO,
                severity=AlertSeverity.ALTA,
                explanation="Coincidencia exacta normalizada disponible",
            ),
            DeterministicRule(
                fact_key="foto_reutilizada",
                signal_type=RiskSignalType.FOTO_REUTILIZADA,
                severity=AlertSeverity.CRITICA,
                explanation="Coincidencia exacta de hash disponible",
            ),
        ),
    )


def get_evaluate_fraud_service() -> EvaluateFraudService:
    return EvaluateFraudService(get_fraud_adapter(), get_fraud_repository())


def get_fraud_alert_service() -> GetFraudAlertService:
    return GetFraudAlertService(get_fraud_repository())


def _alert_response(alert: AlertView) -> AlertaFraudeResponse:
    return AlertaFraudeResponse(
        id=alert.id,
        siniestroId=alert.claim_id,
        tipo=alert.alert_type,
        severidad=alert.severity.value,
        efecto=alert.effect.value,
        estadoRevision=alert.review_status.value,
        nivelDetalle=alert.detail_level.value,
        explicacion=alert.explanation,
        datosOrigen=alert.source_data,
        modeloORegla=alert.rule_or_model,
        versionPolitica=alert.policy_version,
    )


@router.post(
    "/{siniestro_id}/fraude/evaluaciones",
    response_model=EvaluacionFraudeResponse,
)
def evaluate_fraud(
    siniestro_id: int,
    request: EvaluarFraudeRequest,
    idempotency_key: str = Header(alias="Idempotency-Key"),
    principal: AuthenticatedPrincipal = Depends(get_authenticated_principal),
    service: EvaluateFraudService = Depends(get_evaluate_fraud_service),
) -> EvaluacionFraudeResponse:
    try:
        result: FraudEvaluationResult = service.execute(
            EvaluateFraudCommand(siniestro_id, request.hechos),
            principal,
            idempotency_key=idempotency_key,
            request_payload=request.model_dump(mode="json", by_alias=True),
        )
    except FraudEvaluationError as exc:
        raise BusinessError(exc.code, exc.message, exc.status_code) from exc
    alerts = [
        AlertaFraudeResponse(
            id=alert.id,
            siniestroId=alert.claim_id,
            tipo=alert.alert_type,
            severidad=alert.severity.value,
            efecto=alert.effect.value,
            estadoRevision=alert.review_status.value,
            nivelDetalle="detalle",
            explicacion=alert.explanation,
            datosOrigen=alert.source_data,
            modeloORegla=alert.rule_or_model,
            versionPolitica=alert.policy_version,
        )
        for alert in result.alerts
    ]
    return EvaluacionFraudeResponse(siniestroId=result.claim_id, alertas=alerts)


@router.get(
    "/{siniestro_id}/alertas/{alerta_id}",
    response_model=AlertaFraudeResponse,
)
def get_fraud_alert(
    siniestro_id: int,
    alerta_id: int,
    principal: AuthenticatedPrincipal = Depends(get_authenticated_principal),
    service: GetFraudAlertService = Depends(get_fraud_alert_service),
) -> AlertaFraudeResponse:
    try:
        return _alert_response(
            service.execute(siniestro_id, alerta_id, principal)
        )
    except FraudEvaluationError as exc:
        raise BusinessError(exc.code, exc.message, exc.status_code) from exc
