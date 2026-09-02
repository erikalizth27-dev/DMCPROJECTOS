from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from siniestro_facil.api.routes.assistance import (
    get_get_assistance_service,
    get_request_assistance_service,
)
from siniestro_facil.api.routes.claims import get_authenticated_principal
from siniestro_facil.application.request_assistance import (
    GetAssistanceService,
    InMemoryAssistanceRepository,
    RequestAssistanceService,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal
from siniestro_facil.infrastructure.provider_adapter import (
    SimulatedProviderAdapter,
)
from siniestro_facil.main import create_app


def principal() -> AuthenticatedPrincipal:
    now = datetime.now(timezone.utc)
    return AuthenticatedPrincipal(
        subject="operator-assistance-api",
        role=PrincipalRole.OPERADOR,
        actor_type=ActorType.INTERNO,
        tenant_id="tenant-synthetic",
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


def client() -> TestClient:
    repository = InMemoryAssistanceRepository(visible_claim_ids={42})
    app = create_app()
    app.dependency_overrides[get_authenticated_principal] = principal
    app.dependency_overrides[get_request_assistance_service] = lambda: (
        RequestAssistanceService(
            repository,
            SimulatedProviderAdapter(),
        )
    )
    app.dependency_overrides[get_get_assistance_service] = lambda: (
        GetAssistanceService(repository)
    )
    return TestClient(app)


def test_creates_and_gets_assistance() -> None:
    api = client()
    created = api.post(
        "/api/v1/siniestros/42/asistencias",
        headers={"Idempotency-Key": "assistance-api-idem-0001"},
        json={
            "proveedorId": 7,
            "tipoAsistencia": "grua",
            "motivo": "Vehículo inmovilizado",
        },
    )
    assert created.status_code == 201
    body = created.json()
    assert body["estado"] == "enviada"
    fetched = api.get(
        f"/api/v1/siniestros/42/asistencias/{body['id']}"
    )
    assert fetched.status_code == 200
    assert fetched.json() == body


def test_replays_same_api_request() -> None:
    api = client()
    request = {
        "proveedorId": 7,
        "tipoAsistencia": "grua",
        "motivo": "Vehículo inmovilizado",
    }
    headers = {"Idempotency-Key": "assistance-api-idem-0001"}
    first = api.post(
        "/api/v1/siniestros/42/asistencias",
        headers=headers,
        json=request,
    )
    second = api.post(
        "/api/v1/siniestros/42/asistencias",
        headers=headers,
        json=request,
    )
    assert first.status_code == 201
    assert second.status_code == 201
    assert second.json() == first.json()


def test_returns_409_for_other_payload_with_same_key() -> None:
    api = client()
    headers = {"Idempotency-Key": "assistance-api-idem-0001"}
    api.post(
        "/api/v1/siniestros/42/asistencias",
        headers=headers,
        json={
            "proveedorId": 7,
            "tipoAsistencia": "grua",
            "motivo": "Primer motivo",
        },
    )
    response = api.post(
        "/api/v1/siniestros/42/asistencias",
        headers=headers,
        json={
            "proveedorId": 7,
            "tipoAsistencia": "grua",
            "motivo": "Otro motivo",
        },
    )
    assert response.status_code == 409
    assert response.json()["codigo"] == "IDEMPOTENCY-CONFLICT"


def test_hides_assistance_from_other_claim() -> None:
    api = client()
    response = api.get("/api/v1/siniestros/99/asistencias/1")
    assert response.status_code == 404
    assert response.json()["codigo"] == "ASSISTANCE-NOT-FOUND"


def test_requires_authentication() -> None:
    app = create_app()
    response = TestClient(app).post(
        "/api/v1/siniestros/42/asistencias",
        headers={"Idempotency-Key": "assistance-api-idem-0001"},
        json={
            "proveedorId": 7,
            "tipoAsistencia": "grua",
            "motivo": "Vehículo inmovilizado",
        },
    )
    assert response.status_code == 401
