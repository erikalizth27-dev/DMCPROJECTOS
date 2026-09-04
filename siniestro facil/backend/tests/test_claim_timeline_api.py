from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from siniestro_facil.api.routes.claims import get_authenticated_principal
from siniestro_facil.api.routes.timeline import get_claim_timeline_service
from siniestro_facil.application.get_claim_timeline import (
    GetClaimTimelineService,
    TimelineSlice,
)
from siniestro_facil.domain.audit import TimelineEvent
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal
from siniestro_facil.main import create_app


class ApiTimelineRepository:
    def __init__(self, *, visible: bool = True) -> None:
        self.visible = visible
        self.accesses = 0

    def list_visible(
        self, claim_id, principal, *, after_event_id, page_size
    ):
        if not self.visible:
            return None
        return TimelineSlice(
            (
                TimelineEvent(
                    event_id=7,
                    claim_id=claim_id,
                    event_type="pago_preparado",
                    actor_id=2,
                    detail={"monto": "1250.00"},
                    occurred_at=datetime(2026, 9, 3, tzinfo=timezone.utc),
                ),
            ),
            None,
        )

    def record_sensitive_access(
        self, claim_id, principal, *, event_ids
    ) -> None:
        self.accesses += 1


def principal() -> AuthenticatedPrincipal:
    now = datetime.now(timezone.utc)
    return AuthenticatedPrincipal(
        subject="timeline-operator",
        role=PrincipalRole.OPERADOR,
        actor_type=ActorType.INTERNO,
        tenant_id="tenant-s6",
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


def client(*, visible: bool = True) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_authenticated_principal] = principal
    app.dependency_overrides[get_claim_timeline_service] = lambda: (
        GetClaimTimelineService(ApiTimelineRepository(visible=visible))
    )
    return TestClient(app)


def test_returns_ordered_timeline_contract() -> None:
    response = client().get(
        "/api/v1/siniestros/4/linea-tiempo",
        params={"despuesDe": 0, "cantidad": 10},
    )
    assert response.status_code == 200
    assert response.json() == {
        "siniestroId": 4,
        "nivelDetalle": "operativo",
        "eventos": [
            {
                "id": 7,
                "tipoEvento": "pago_preparado",
                "actorId": 2,
                "fecha": "2026-09-03T00:00:00Z",
                "detalle": {"monto": "1250.00"},
                "nivelDetalle": "operativo",
            }
        ],
        "siguienteCursor": None,
    }


def test_private_not_found_is_preserved() -> None:
    response = client(visible=False).get(
        "/api/v1/siniestros/4/linea-tiempo"
    )
    assert response.status_code == 404
    assert response.json()["codigo"] == "CLAIM-TIMELINE-NOT-FOUND"


def test_invalid_query_is_rejected_by_api() -> None:
    response = client().get(
        "/api/v1/siniestros/4/linea-tiempo",
        params={"cantidad": 0},
    )
    assert response.status_code == 422


def test_authentication_is_required_by_default() -> None:
    app = create_app()
    app.dependency_overrides[get_claim_timeline_service] = lambda: (
        GetClaimTimelineService(ApiTimelineRepository())
    )
    response = TestClient(app).get(
        "/api/v1/siniestros/4/linea-tiempo"
    )
    assert response.status_code == 401
