from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from siniestro_facil.api.routes.claims import get_authenticated_principal
from siniestro_facil.api.routes.payments import (
    get_authorize_payment_service,
    get_prepare_payment_service,
)
from siniestro_facil.application.manage_payment import (
    AuthorizePaymentService,
    InMemoryPaymentRepository,
    PreparePaymentService,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import (
    ActorType,
    AuthenticatedPrincipal,
)
from siniestro_facil.infrastructure.payment_adapter import (
    DeterministicPaymentAdapter,
)
from siniestro_facil.main import create_app


PREPARE_HEADERS = {"Idempotency-Key": "payment-api-prepare-0001"}
AUTHORIZE_HEADERS = {"Idempotency-Key": "payment-api-authorize-0001"}


def principal(
    role: PrincipalRole,
    *,
    subject: str | None = None,
) -> AuthenticatedPrincipal:
    now = datetime.now(timezone.utc)
    return AuthenticatedPrincipal(
        subject=subject or f"{role.value}-payment-api",
        role=role,
        actor_type=ActorType.INTERNO,
        tenant_id="tenant-synthetic",
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


def configured_client(
    *,
    repository: InMemoryPaymentRepository | None = None,
    role: PrincipalRole = PrincipalRole.OPERADOR,
):
    app = create_app()
    repository = repository or InMemoryPaymentRepository()
    actor = {"value": principal(role)}
    app.dependency_overrides[get_authenticated_principal] = (
        lambda: actor["value"]
    )
    app.dependency_overrides[get_prepare_payment_service] = (
        lambda: PreparePaymentService(repository)
    )
    app.dependency_overrides[get_authorize_payment_service] = (
        lambda: AuthorizePaymentService(
            repository,
            DeterministicPaymentAdapter(version="pilot-1"),
        )
    )
    return TestClient(app), actor


def prepare(client: TestClient):
    return client.post(
        "/api/v1/siniestros/42/pagos",
        json={"monto": "125.50"},
        headers=PREPARE_HEADERS,
    )


def test_operator_prepares_payment() -> None:
    client, _ = configured_client()
    response = prepare(client)
    assert response.status_code == 201
    body = response.json()
    assert body["siniestroId"] == 42
    assert body["estado"] == "bloqueado"
    assert body["transferenciaRealizada"] is False
    assert body["version"] == 0


def test_prepare_repeats_idempotently() -> None:
    client, _ = configured_client()
    first = prepare(client)
    repeated = prepare(client)
    assert first.status_code == 201
    assert repeated.status_code == 201
    assert repeated.json() == first.json()


def test_insured_cannot_prepare_payment() -> None:
    client, _ = configured_client(role=PrincipalRole.ASEGURADO)
    response = prepare(client)
    assert response.status_code == 403
    assert response.json()["codigo"] == "PAYMENT-PREPARE-FORBIDDEN"


def test_supervisor_authorizes_payment() -> None:
    client, actor = configured_client()
    prepared = prepare(client).json()
    actor["value"] = principal(
        PrincipalRole.SUPERVISOR,
        subject="supervisor-payment-api",
    )
    response = client.post(
        f"/api/v1/siniestros/42/pagos/{prepared['id']}/autorizacion",
        json={"version": prepared["version"]},
        headers=AUTHORIZE_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()["estado"] == "emitido"
    assert response.json()["transferenciaRealizada"] is False
    assert response.json()["autorizadoPor"] == "supervisor-payment-api"


def test_critical_alert_blocks_authorization() -> None:
    repository = InMemoryPaymentRepository(
        critical_alert_claims={42}
    )
    client, actor = configured_client(repository=repository)
    prepared = prepare(client).json()
    actor["value"] = principal(PrincipalRole.SUPERVISOR)
    response = client.post(
        f"/api/v1/siniestros/42/pagos/{prepared['id']}/autorizacion",
        json={"version": 0},
        headers=AUTHORIZE_HEADERS,
    )
    assert response.status_code == 409
    assert (
        response.json()["codigo"]
        == "PAYMENT-BLOCKED-BY-CRITICAL-ALERT"
    )


def test_payment_requires_authentication_by_default() -> None:
    response = TestClient(create_app()).post(
        "/api/v1/siniestros/42/pagos",
        json={"monto": "125.50"},
        headers=PREPARE_HEADERS,
    )
    assert response.status_code == 401
