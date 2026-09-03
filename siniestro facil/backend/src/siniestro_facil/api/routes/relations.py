from __future__ import annotations

from functools import lru_cache

from fastapi import APIRouter, Depends, Header
from pydantic import Field

from siniestro_facil.api.errors import BusinessError
from siniestro_facil.api.routes.claims import get_authenticated_principal
from siniestro_facil.api.schemas import ApiModel
from siniestro_facil.application.detect_case_relations import (
    CandidateCaseFacts,
    CaseRelationError,
    CaseRelationResult,
    DetectCaseRelationsCommand,
    DetectCaseRelationsService,
    InMemoryCaseRelationRepository,
)
from siniestro_facil.config import Settings
from siniestro_facil.db import create_database_engine
from siniestro_facil.domain.fraud import RelationCriterion
from siniestro_facil.domain.identity import AuthenticatedPrincipal
from siniestro_facil.persistence.case_relation_repository import (
    PostgreSQLCaseRelationRepository,
)
from siniestro_facil.persistence.session import create_session_factory


router = APIRouter(prefix="/api/v1/siniestros", tags=["Fraude"])


class CasoCandidatoRequest(ApiModel):
    siniestro_id: int = Field(alias="siniestroId", gt=0)
    valores: dict[RelationCriterion, str | None]


class DetectarRelacionesRequest(ApiModel):
    valores: dict[RelationCriterion, str | None]
    candidatos: list[CasoCandidatoRequest] = Field(min_length=1)


class RelacionCandidataResponse(ApiModel):
    id: int
    siniestro_a: int = Field(alias="siniestroA")
    siniestro_b: int = Field(alias="siniestroB")
    criterio: str
    valor_normalizado: str = Field(alias="valorNormalizado")
    estado_revision: str = Field(alias="estadoRevision")


class RelacionesDetectadasResponse(ApiModel):
    siniestro_id: int = Field(alias="siniestroId")
    relaciones: list[RelacionCandidataResponse]


@lru_cache(maxsize=1)
def get_case_relation_repository():
    settings = Settings.from_environment()
    if not settings.database_url:
        return InMemoryCaseRelationRepository()
    engine = create_database_engine(settings)
    return PostgreSQLCaseRelationRepository(create_session_factory(engine))


def get_detect_case_relations_service() -> DetectCaseRelationsService:
    return DetectCaseRelationsService(get_case_relation_repository())


@router.post(
    "/{siniestro_id}/relaciones/detectar",
    response_model=RelacionesDetectadasResponse,
)
def detect_case_relations(
    siniestro_id: int,
    request: DetectarRelacionesRequest,
    idempotency_key: str = Header(alias="Idempotency-Key"),
    principal: AuthenticatedPrincipal = Depends(get_authenticated_principal),
    service: DetectCaseRelationsService = Depends(
        get_detect_case_relations_service
    ),
) -> RelacionesDetectadasResponse:
    try:
        result: CaseRelationResult = service.execute(
            DetectCaseRelationsCommand(
                claim_id=siniestro_id,
                own_values=request.valores,
                candidates=tuple(
                    CandidateCaseFacts(
                        claim_id=item.siniestro_id,
                        values=item.valores,
                    )
                    for item in request.candidatos
                ),
            ),
            principal,
            idempotency_key=idempotency_key,
            request_payload=request.model_dump(mode="json", by_alias=True),
        )
    except CaseRelationError as exc:
        raise BusinessError(exc.code, exc.message, exc.status_code) from exc
    return RelacionesDetectadasResponse(
        siniestroId=result.claim_id,
        relaciones=[
            RelacionCandidataResponse(
                id=item.id,
                siniestroA=item.claim_a,
                siniestroB=item.claim_b,
                criterio=item.criterion.value,
                valorNormalizado=item.normalized_value,
                estadoRevision=item.review_status,
            )
            for item in result.relations
        ],
    )
