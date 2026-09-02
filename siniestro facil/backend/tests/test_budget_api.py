from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from siniestro_facil.api.routes.claims import get_authenticated_principal
from siniestro_facil.api.routes.inspections import (
    get_get_budget_service,
    get_submit_budget_service,
)
from siniestro_facil.application.submit_budget import (
    GetBudgetService,
    InMemoryBudgetSubmissionRepository,
    SubmitBudgetService,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal
from siniestro_facil.main import create_app


def taller_principal() -> AuthenticatedPrincipal:
    now = datetime.now(timezone.utc)
    return AuthenticatedPrincipal(
        subject="taller-budget-synthetic",
        role=PrincipalRole.TALLER,
        actor_type=ActorType.PROVEEDOR,
        tenant_id="tenant-synthetic",
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


def configured_client() -> TestClient:
    repository = InMemoryBudgetSubmissionRepository()
    app = create_app()
    app.dependency_overrides[get_authenticated_principal] = taller_principal
    app.dependency_overrides[get_submit_budget_service] = (
        lambda: SubmitBudgetService(repository)
    )
    app.dependency_overrides[get_get_budget_service] = (
        lambda: GetBudgetService(repository)
    )
    return TestClient(app)


def payload() -> dict[str, object]:
    return {
        "diagnostico": "Daño frontal sujeto a revisión",
        "fechaPresentacion": "2026-09-02",
        "version": 4,
    }


def test_submits_and_gets_budget() -> None:
    client = configured_client()
    created = client.post(
        "/api/v1/siniestros/42/inspecciones/7/presupuestos",
        json=payload(),
    )

    assert created.status_code == 201
    body = created.json()
    assert body["siniestroId"] == 42
    assert body["inspeccionId"] == 7
    assert body["diagnostico"] == payload()["diagnostico"]
    assert body["vigenciaDesde"] == "2026-09-02"
    assert body["vigenciaHasta"] == "2026-09-17"
    assert body["estado"] == "recibido"
    assert body["estadoActual"] == "presupuesto_recibido"
    assert body["version"] == 5

    found = client.get(
        f"/api/v1/siniestros/42/presupuestos/{body['id']}"
    )
    assert found.status_code == 200
    assert found.json() == body


def test_requires_diagnosis() -> None:
    response = configured_client().post(
        "/api/v1/siniestros/42/inspecciones/7/presupuestos",
        json={**payload(), "diagnostico": ""},
    )

    assert response.status_code == 422


def test_hides_budget_from_unrelated_claim() -> None:
    client = configured_client()
    created = client.post(
        "/api/v1/siniestros/42/inspecciones/7/presupuestos",
        json=payload(),
    )
    response = client.get(
        f"/api/v1/siniestros/99/presupuestos/{created.json()['id']}"
    )

    assert response.status_code == 404
    assert response.json()["codigo"] == "BUDGET-NOT-FOUND"


def test_requires_authentication_by_default() -> None:
    response = TestClient(create_app()).post(
        "/api/v1/siniestros/42/inspecciones/7/presupuestos",
        json=payload(),
    )

    assert response.status_code == 401
