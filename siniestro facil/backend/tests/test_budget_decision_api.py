from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from siniestro_facil.api.routes.claims import get_authenticated_principal
from siniestro_facil.api.routes.inspections import get_decide_budget_service
from siniestro_facil.application.decide_budget import (
    DecideBudgetService,
    InMemoryBudgetDecisionRepository,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal
from siniestro_facil.main import create_app


def principal(role: PrincipalRole) -> AuthenticatedPrincipal:
    now = datetime.now(timezone.utc)
    return AuthenticatedPrincipal(
        subject=f"{role.value}-budget-decision-api",
        role=role,
        actor_type=ActorType.INTERNO,
        tenant_id="tenant-synthetic",
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


def configured_client(role: PrincipalRole) -> TestClient:
    app = create_app()
    repository = InMemoryBudgetDecisionRepository()
    app.dependency_overrides[get_authenticated_principal] = (
        lambda: principal(role)
    )
    app.dependency_overrides[get_decide_budget_service] = (
        lambda: DecideBudgetService(repository)
    )
    return TestClient(app)


def payload(decision: str = "autorizado") -> dict[str, object]:
    return {
        "decision": decision,
        "justificacion": "Decisión formal documentada",
        "version": 5,
    }


def test_supervisor_authorizes_budget() -> None:
    response = configured_client(PrincipalRole.SUPERVISOR).post(
        "/api/v1/siniestros/42/presupuestos/7/decision",
        json=payload(),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["presupuestoId"] == 7
    assert body["siniestroId"] == 42
    assert body["decision"] == "autorizado"
    assert body["estadoActual"] == "autorizado"
    assert body["version"] == 6


def test_assigned_operator_observes_budget() -> None:
    response = configured_client(PrincipalRole.OPERADOR).post(
        "/api/v1/siniestros/42/presupuestos/7/decision",
        json=payload("observado"),
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "observado"
    assert response.json()["estadoActual"] == "observado"


def test_operator_cannot_authorize_budget() -> None:
    response = configured_client(PrincipalRole.OPERADOR).post(
        "/api/v1/siniestros/42/presupuestos/7/decision",
        json=payload(),
    )

    assert response.status_code == 403
    assert response.json()["codigo"] == "BUDGET-DECISION-FORBIDDEN"


def test_requires_authentication_by_default() -> None:
    response = TestClient(create_app()).post(
        "/api/v1/siniestros/42/presupuestos/7/decision",
        json=payload(),
    )

    assert response.status_code == 401
