from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from siniestro_facil.api.routes.claims import get_authenticated_principal
from siniestro_facil.api.routes.metrics import get_operational_metrics_service
from siniestro_facil.application.get_operational_metrics import (
    GetOperationalMetricsService,
    OperationalMetricFacts,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal
from siniestro_facil.main import create_app


class ApiFactsRepository:
    def load_facts(self, *, period_start, period_end, principal):
        return OperationalMetricFacts(
            claim_created_at=period_start,
            first_assistance_at=period_start + timedelta(minutes=2),
            first_decision_at=None,
            source_claim_id=4,
        )


def supervisor() -> AuthenticatedPrincipal:
    now = datetime.now(timezone.utc)
    return AuthenticatedPrincipal(
        subject="metrics-supervisor",
        role=PrincipalRole.SUPERVISOR,
        actor_type=ActorType.INTERNO,
        tenant_id="tenant-s6",
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


def client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_authenticated_principal] = supervisor
    app.dependency_overrides[get_operational_metrics_service] = lambda: (
        GetOperationalMetricsService(ApiFactsRepository())
    )
    return TestClient(app)


def test_returns_period_sources_and_availability() -> None:
    response = client().get(
        "/api/v1/indicadores/operativos",
        params={
            "desde": "2026-09-01T00:00:00Z",
            "hasta": "2026-09-02T00:00:00Z",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["siniestroFuenteId"] == 4
    assert payload["periodo"]["desde"] == "2026-09-01T00:00:00Z"
    assert payload["indicadores"][0]["valorSegundos"] == 120
    assert payload["indicadores"][0]["fuentes"] == [
        "siniestro.creado_en",
        "asistencia.creado_en",
    ]
    assert payload["indicadores"][1]["disponibilidad"] == "no_disponible"
    assert payload["indicadores"][1]["valorSegundos"] is None


def test_period_is_required() -> None:
    response = client().get("/api/v1/indicadores/operativos")
    assert response.status_code == 422


def test_authentication_is_required() -> None:
    app = create_app()
    app.dependency_overrides[get_operational_metrics_service] = lambda: (
        GetOperationalMetricsService(ApiFactsRepository())
    )
    response = TestClient(app).get(
        "/api/v1/indicadores/operativos",
        params={
            "desde": "2026-09-01T00:00:00Z",
            "hasta": "2026-09-02T00:00:00Z",
        },
    )
    assert response.status_code == 401
