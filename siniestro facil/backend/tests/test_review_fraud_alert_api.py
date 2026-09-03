from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from siniestro_facil.api.routes.claims import get_authenticated_principal
from siniestro_facil.api.routes.fraud import (
    get_evaluate_fraud_service,
    get_review_fraud_alert_service,
)
from siniestro_facil.application.evaluate_fraud import (
    EvaluateFraudService,
    InMemoryFraudAlertRepository,
    ReviewFraudAlertService,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.fraud import AlertSeverity, RiskSignalType
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal
from siniestro_facil.infrastructure.fraud_adapter import (
    DeterministicFraudAdapter,
    DeterministicRule,
)
from siniestro_facil.main import create_app


def principal(role: PrincipalRole) -> AuthenticatedPrincipal:
    now = datetime.now(timezone.utc)
    return AuthenticatedPrincipal(
        subject=f"{role.value}-review-api",
        role=role,
        actor_type=ActorType.INTERNO,
        tenant_id="tenant-synthetic",
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


def client_with_alert(role=PrincipalRole.INVESTIGADOR_FRAUDE):
    app = create_app()
    repository = InMemoryFraudAlertRepository()
    adapter = DeterministicFraudAdapter(
        rule_set="pilot",
        version="1",
        policy_version="policy-1",
        rules=(
            DeterministicRule(
                "foto_reutilizada",
                RiskSignalType.FOTO_REUTILIZADA,
                AlertSeverity.CRITICA,
                "Hash exacto repetido",
            ),
        ),
    )
    app.dependency_overrides[get_authenticated_principal] = lambda: principal(
        PrincipalRole.INVESTIGADOR_FRAUDE
    )
    app.dependency_overrides[get_evaluate_fraud_service] = lambda: (
        EvaluateFraudService(adapter, repository)
    )
    app.dependency_overrides[get_review_fraud_alert_service] = lambda: (
        ReviewFraudAlertService(repository)
    )
    client = TestClient(app)
    created = client.post(
        "/api/v1/siniestros/42/fraude/evaluaciones",
        json={"hechos": {"foto_reutilizada": True}},
        headers={"Idempotency-Key": "fraud-review-api-setup"},
    )
    alert_id = created.json()["alertas"][0]["id"]
    app.dependency_overrides[get_authenticated_principal] = lambda: principal(role)
    return client, alert_id


def review(client, alert_id, *, state="confirmada", key="fraud-review-api-0001"):
    return client.patch(
        f"/api/v1/siniestros/42/alertas/{alert_id}/revision",
        json={
            "estado": state,
            "justificacion": "Decisión humana documentada",
            "version": 0,
        },
        headers={"Idempotency-Key": key},
    )


def test_investigator_confirms_alert() -> None:
    client, alert_id = client_with_alert()
    response = review(client, alert_id)
    assert response.status_code == 200
    assert response.json()["estadoRevision"] == "confirmada"
    assert response.json()["version"] == 1


def test_repeated_review_returns_same_response() -> None:
    client, alert_id = client_with_alert()
    first = review(client, alert_id)
    repeated = review(client, alert_id)
    assert repeated.status_code == 200
    assert repeated.json() == first.json()


def test_changed_review_conflicts() -> None:
    client, alert_id = client_with_alert()
    review(client, alert_id)
    response = review(client, alert_id, state="descartada")
    assert response.status_code == 409
    assert response.json()["codigo"] == "IDEMPOTENCY-CONFLICT"


def test_operator_cannot_review_alert() -> None:
    client, alert_id = client_with_alert(PrincipalRole.OPERADOR)
    response = review(client, alert_id)
    assert response.status_code == 403
    assert response.json()["codigo"] == "ALERT-REVIEW-FORBIDDEN"
