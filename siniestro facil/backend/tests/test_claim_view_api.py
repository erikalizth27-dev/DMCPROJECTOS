from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from siniestro_facil.api.routes.claims import (
    get_authenticated_principal,
    get_claim_view_service,
)
from siniestro_facil.application.get_claim_view import ClaimView, GetClaimViewService
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal
from siniestro_facil.main import create_app


class VisibleRepository:
    def __init__(self, visible=True):
        self.visible = visible

    def find_visible(self, claim_id, principal):
        if not self.visible:
            return None
        return ClaimView(
            id=claim_id,
            estado_actual="reportado",
            fecha_evento=datetime(2026, 8, 25, tzinfo=timezone.utc),
            tipo_evento="colision",
            siguiente_paso="validar_cobertura",
        )


def make_principal(role=PrincipalRole.ASEGURADO):
    now = datetime.now(timezone.utc)
    return AuthenticatedPrincipal(
        subject="subject-synthetic",
        role=role,
        actor_type=ActorType.EXTERNO,
        tenant_id="tenant-synthetic",
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


def client(visible=True):
    app = create_app()
    app.dependency_overrides[get_authenticated_principal] = make_principal
    app.dependency_overrides[get_claim_view_service] = lambda: GetClaimViewService(
        VisibleRepository(visible)
    )
    return TestClient(app)


def test_returns_initial_claim_view() -> None:
    response = client().get("/api/v1/siniestros/42")
    assert response.status_code == 200
    assert response.json()["id"] == 42
    assert response.json()["siguientePaso"] == "validar_cobertura"


def test_out_of_scope_uses_private_not_found_response() -> None:
    response = client(visible=False).get("/api/v1/siniestros/42")
    assert response.status_code == 404
    assert response.json()["codigo"] == "CLAIM-NOT-FOUND"
    assert response.json()["detalles"] == []


def test_missing_authentication_is_denied_by_default() -> None:
    app = create_app()
    app.dependency_overrides[get_claim_view_service] = lambda: GetClaimViewService(
        VisibleRepository()
    )
    response = TestClient(app).get("/api/v1/siniestros/42")
    assert response.status_code == 401
    assert response.json()["codigo"] == "AUTHENTICATION-REQUIRED"
