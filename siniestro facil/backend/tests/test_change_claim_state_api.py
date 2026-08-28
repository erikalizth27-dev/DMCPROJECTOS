from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from siniestro_facil.api.routes.claims import (
    get_authenticated_principal,
    get_change_claim_state_service,
)
from siniestro_facil.application.change_claim_state import (
    ChangedClaimState,
    ChangeClaimStateService,
    ClaimStateChangeError,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.enums import EstadoSiniestro
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal
from siniestro_facil.main import create_app


class ApiStateRepository:
    def __init__(self, error: ClaimStateChangeError | None = None) -> None:
        self.error = error
        self.last_command = None

    def change_state(self, command, principal):
        self.last_command = command
        if self.error is not None:
            raise self.error
        return ChangedClaimState(
            id=command.claim_id,
            current_state=command.target_state,
            version=command.expected_version + 1,
        )


def principal() -> AuthenticatedPrincipal:
    now = datetime.now(timezone.utc)
    return AuthenticatedPrincipal(
        subject="operator-synthetic",
        role=PrincipalRole.OPERADOR,
        actor_type=ActorType.INTERNO,
        tenant_id="tenant-synthetic",
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


def client(repository: ApiStateRepository) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_authenticated_principal] = principal
    app.dependency_overrides[get_change_claim_state_service] = (
        lambda: ChangeClaimStateService(repository)
    )
    return TestClient(app)


def test_changes_claim_state_with_http_200() -> None:
    repository = ApiStateRepository()
    response = client(repository).post(
        "/api/v1/siniestros/42/estado",
        json={
            "estadoDestino": "validando_cobertura",
            "motivo": "Iniciar validación",
            "version": 0,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": 42,
        "estadoActual": "validando_cobertura",
        "version": 1,
    }


def test_maps_version_conflict_to_private_http_409() -> None:
    response = client(
        ApiStateRepository(
            ClaimStateChangeError(
                "STATE-VERSION-CONFLICT",
                "La versión del siniestro está desactualizada",
                409,
            )
        )
    ).post(
        "/api/v1/siniestros/42/estado",
        json={
            "estadoDestino": "validando_cobertura",
            "motivo": "Iniciar validación",
            "version": 0,
        },
    )
    assert response.status_code == 409
    assert response.json()["codigo"] == "STATE-VERSION-CONFLICT"
    assert response.json()["detalles"] == []


def test_rejects_invalid_transition_contract() -> None:
    response = client(
        ApiStateRepository(
            ClaimStateChangeError(
                "INVALID-TRANSITION",
                "Transición no permitida",
                409,
            )
        )
    ).post(
        "/api/v1/siniestros/42/estado",
        json={
            "estadoDestino": "cerrado",
            "motivo": "Intento inválido",
            "version": 0,
        },
    )
    assert response.status_code == 409
    assert response.json()["codigo"] == "INVALID-TRANSITION"


def test_requires_authentication_by_default() -> None:
    app = create_app()
    app.dependency_overrides[get_change_claim_state_service] = (
        lambda: ChangeClaimStateService(ApiStateRepository())
    )
    response = TestClient(app).post(
        "/api/v1/siniestros/42/estado",
        json={
            "estadoDestino": "validando_cobertura",
            "motivo": "Iniciar validación",
            "version": 0,
        },
    )
    assert response.status_code == 401
    assert response.json()["codigo"] == "AUTHENTICATION-REQUIRED"
