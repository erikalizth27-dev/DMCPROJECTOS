from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from siniestro_facil.api.routes.assistance import (
    get_reassign_assistance_service,
    get_register_provider_reply_service,
)
from siniestro_facil.api.routes.claims import get_authenticated_principal
from siniestro_facil.application.assistance_contracts import AssistanceRecord
from siniestro_facil.application.manage_assistance import (
    InMemoryAssistanceManagementRepository,
    ReassignAssistanceService,
    RegisterProviderReplyService,
)
from siniestro_facil.domain.assistance import AssistanceStatus
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal
from siniestro_facil.main import create_app


def principal() -> AuthenticatedPrincipal:
    now = datetime.now(timezone.utc)
    return AuthenticatedPrincipal(
        subject="operator-management-api",
        role=PrincipalRole.OPERADOR,
        actor_type=ActorType.INTERNO,
        tenant_id="tenant-synthetic",
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


def client(
    status: AssistanceStatus = AssistanceStatus.SENT,
    attempt: int = 1,
) -> TestClient:
    now = datetime.now(timezone.utc)
    repository = InMemoryAssistanceManagementRepository(
        [
            AssistanceRecord(
                id=10,
                claim_id=42,
                provider_id=7,
                assistance_type="grua",
                status=status,
                attempt=attempt,
                created_at=now,
                updated_at=now,
            )
        ],
        visible_claim_ids={42},
    )
    app = create_app()
    app.dependency_overrides[get_authenticated_principal] = principal
    app.dependency_overrides[
        get_register_provider_reply_service
    ] = lambda: RegisterProviderReplyService(repository)
    app.dependency_overrides[
        get_reassign_assistance_service
    ] = lambda: ReassignAssistanceService(repository)
    return TestClient(app)


def test_registers_accepted_provider_reply() -> None:
    response = client().post(
        "/api/v1/siniestros/42/asistencias/10/respuesta",
        json={
            "resultado": "aceptada",
            "intentoEsperado": 1,
            "referenciaExterna": "PROVIDER-0001",
        },
    )
    assert response.status_code == 200
    assert response.json()["estado"] == "aceptada"
    assert response.json()["numeroIntento"] == 1


def test_returns_409_for_stale_attempt() -> None:
    response = client(attempt=2).post(
        "/api/v1/siniestros/42/asistencias/10/respuesta",
        json={
            "resultado": "rechazada",
            "intentoEsperado": 1,
        },
    )
    assert response.status_code == 409
    assert response.json()["codigo"] == "ASSISTANCE-VERSION-CONFLICT"


def test_reassigns_after_no_response() -> None:
    response = client(AssistanceStatus.NO_RESPONSE).post(
        "/api/v1/siniestros/42/asistencias/10/reasignacion",
        json={
            "nuevoProveedorId": 8,
            "intentoEsperado": 1,
            "motivo": "Proveedor sin respuesta",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["proveedorId"] == 8
    assert body["estado"] == "pendiente"
    assert body["numeroIntento"] == 2


def test_rejects_same_provider_reassignment() -> None:
    response = client(AssistanceStatus.REJECTED).post(
        "/api/v1/siniestros/42/asistencias/10/reasignacion",
        json={
            "nuevoProveedorId": 7,
            "intentoEsperado": 1,
            "motivo": "Proveedor rechazó",
        },
    )
    assert response.status_code == 422
    assert response.json()["codigo"] == "PROVIDER-INVALID"


def test_hides_management_endpoint_without_authentication() -> None:
    app = create_app()
    response = TestClient(app).post(
        "/api/v1/siniestros/42/asistencias/10/respuesta",
        json={
            "resultado": "aceptada",
            "intentoEsperado": 1,
        },
    )
    assert response.status_code == 401
