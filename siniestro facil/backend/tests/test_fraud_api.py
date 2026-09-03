from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from siniestro_facil.api.routes.claims import get_authenticated_principal
from siniestro_facil.api.routes.fraud import (
    get_evaluate_fraud_service,
    get_fraud_alert_service,
)
from siniestro_facil.application.evaluate_fraud import (
    EvaluateFraudService,
    GetFraudAlertService,
    InMemoryFraudAlertRepository,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.fraud import AlertSeverity, RiskSignalType
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal
from siniestro_facil.infrastructure.fraud_adapter import (
    DeterministicFraudAdapter,
    DeterministicRule,
)
from siniestro_facil.main import create_app


HEADERS = {"Idempotency-Key": "fraud-evaluation-api-0001"}


def principal(role: PrincipalRole) -> AuthenticatedPrincipal:
    now = datetime.now(timezone.utc)
    return AuthenticatedPrincipal(
        subject=f"{role.value}-fraud-api",
        role=role,
        actor_type=ActorType.INTERNO,
        tenant_id="tenant-synthetic",
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


def configured_client(role: PrincipalRole) -> TestClient:
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
    app.dependency_overrides[get_authenticated_principal] = lambda: principal(role)
    app.dependency_overrides[get_evaluate_fraud_service] = lambda: (
        EvaluateFraudService(adapter, repository)
    )
    app.dependency_overrides[get_fraud_alert_service] = lambda: (
        GetFraudAlertService(repository)
    )
    return TestClient(app)


def test_investigator_generates_reproducible_alert() -> None:
    response = configured_client(PrincipalRole.INVESTIGADOR_FRAUDE).post(
        "/api/v1/siniestros/42/fraude/evaluaciones",
        json={"hechos": {"foto_reutilizada": True}},
        headers=HEADERS,
    )
    assert response.status_code == 200
    alert = response.json()["alertas"][0]
    assert alert["severidad"] == "critica"
    assert alert["efecto"] == "bloquear_pago_hasta_revision"
    assert alert["modeloORegla"] == "pilot:1"


def test_evaluation_repeats_idempotently() -> None:
    client = configured_client(PrincipalRole.INVESTIGADOR_FRAUDE)
    first = client.post(
        "/api/v1/siniestros/42/fraude/evaluaciones",
        json={"hechos": {"foto_reutilizada": True}},
        headers=HEADERS,
    )
    repeated = client.post(
        "/api/v1/siniestros/42/fraude/evaluaciones",
        json={"hechos": {"foto_reutilizada": True}},
        headers=HEADERS,
    )
    assert repeated.status_code == 200
    assert repeated.json() == first.json()


def test_operator_cannot_trigger_evaluation() -> None:
    response = configured_client(PrincipalRole.OPERADOR).post(
        "/api/v1/siniestros/42/fraude/evaluaciones",
        json={"hechos": {"foto_reutilizada": True}},
        headers=HEADERS,
    )
    assert response.status_code == 403
    assert response.json()["codigo"] == "FRAUD-EVALUATION-FORBIDDEN"


def test_operator_reads_only_summary() -> None:
    client = configured_client(PrincipalRole.INVESTIGADOR_FRAUDE)
    created = client.post(
        "/api/v1/siniestros/42/fraude/evaluaciones",
        json={"hechos": {"foto_reutilizada": True}},
        headers=HEADERS,
    )
    alert_id = created.json()["alertas"][0]["id"]
    app = client.app
    app.dependency_overrides[get_authenticated_principal] = lambda: principal(
        PrincipalRole.OPERADOR
    )
    response = client.get(f"/api/v1/siniestros/42/alertas/{alert_id}")
    assert response.status_code == 200
    assert response.json()["nivelDetalle"] == "resumen"
    assert response.json()["explicacion"] is None
    assert response.json()["datosOrigen"] is None


def test_requires_authentication_by_default() -> None:
    response = TestClient(create_app()).post(
        "/api/v1/siniestros/42/fraude/evaluaciones",
        json={"hechos": {"foto_reutilizada": True}},
        headers=HEADERS,
    )
    assert response.status_code == 401
