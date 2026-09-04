from __future__ import annotations

from functools import lru_cache

from fastapi import APIRouter, Depends, Query

from siniestro_facil.api.errors import BusinessError
from siniestro_facil.api.routes.claims import get_authenticated_principal
from siniestro_facil.application.get_claim_timeline import (
    ClaimTimelineError,
    GetClaimTimelineService,
)
from siniestro_facil.config import Settings
from siniestro_facil.db import create_database_engine
from siniestro_facil.domain.identity import AuthenticatedPrincipal
from siniestro_facil.persistence.claim_timeline_repository import (
    PostgreSQLClaimTimelineRepository,
)
from siniestro_facil.persistence.session import create_session_factory


router = APIRouter(
    prefix="/api/v1/siniestros",
    tags=["Auditoría"],
)


@lru_cache(maxsize=1)
def get_claim_timeline_service() -> GetClaimTimelineService:
    settings = Settings.from_environment()
    if not settings.database_url:
        raise BusinessError(
            "SERVICE-NOT-READY",
            "Servicio de línea de tiempo no disponible",
            503,
        )
    engine = create_database_engine(settings)
    repository = PostgreSQLClaimTimelineRepository(
        create_session_factory(engine)
    )
    return GetClaimTimelineService(repository)


@router.get(
    "/{siniestro_id}/linea-tiempo",
)
def get_claim_timeline(
    siniestro_id: int,
    despues_de: int = Query(default=0, alias="despuesDe", ge=0),
    cantidad: int | None = Query(default=None, gt=0),
    principal: AuthenticatedPrincipal = Depends(get_authenticated_principal),
    service: GetClaimTimelineService = Depends(get_claim_timeline_service),
) -> dict[str, object]:
    try:
        result = service.execute(
            siniestro_id,
            principal,
            after_event_id=despues_de,
            page_size=cantidad,
        )
    except ClaimTimelineError as exc:
        raise BusinessError(exc.code, exc.message, exc.status_code) from exc

    return {
        "siniestroId": result.claim_id,
        "nivelDetalle": result.detail_level.value,
        "eventos": [
            {
                "id": event.event_id,
                "tipoEvento": event.event_type,
                "actorId": event.actor_id,
                "fecha": event.occurred_at,
                "detalle": dict(event.detail),
                "nivelDetalle": event.detail_level.value,
            }
            for event in result.events
        ],
        "siguienteCursor": result.next_cursor,
    }
