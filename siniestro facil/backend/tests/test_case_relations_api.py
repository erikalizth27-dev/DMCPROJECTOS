from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from siniestro_facil.api.routes.claims import get_authenticated_principal
from siniestro_facil.api.routes.relations import (
    get_detect_case_relations_service,
)
from siniestro_facil.application.detect_case_relations import (
    DetectCaseRelationsService,
    InMemoryCaseRelationRepository,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal
from siniestro_facil.main import create_app


def principal(role):
    now = datetime.now(timezone.utc)
    return AuthenticatedPrincipal(
        subject=f"{role.value}-relations-api",
        role=role,
        actor_type=ActorType.INTERNO,
        tenant_id="tenant-synthetic",
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


def configured_client(role=PrincipalRole.INVESTIGADOR_FRAUDE):
    app = create_app()
    repository = InMemoryCaseRelationRepository()
    app.dependency_overrides[get_authenticated_principal] = lambda: principal(role)
    app.dependency_overrides[get_detect_case_relations_service] = lambda: (
        DetectCaseRelationsService(repository)
    )
    return TestClient(app)


PAYLOAD = {
    "valores": {"telefono": " 809 555 0101 "},
    "candidatos": [
        {
            "siniestroId": 7,
            "valores": {"telefono": "809 555 0101"},
        }
    ],
}
HEADERS = {"Idempotency-Key": "case-relations-api-0001"}


def test_detects_exact_normalized_relation() -> None:
    response = configured_client().post(
        "/api/v1/siniestros/42/relaciones/detectar",
        json=PAYLOAD,
        headers=HEADERS,
    )
    assert response.status_code == 200
    relation = response.json()["relaciones"][0]
    assert relation["siniestroA"] == 7
    assert relation["siniestroB"] == 42
    assert relation["criterio"] == "telefono"
    assert relation["estadoRevision"] == "pendiente_revision"


def test_missing_candidate_value_creates_no_relation() -> None:
    payload = {
        **PAYLOAD,
        "candidatos": [
            {"siniestroId": 7, "valores": {"telefono": None}}
        ],
    }
    response = configured_client().post(
        "/api/v1/siniestros/42/relaciones/detectar",
        json=payload,
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json()["relaciones"] == []


def test_repetition_is_idempotent() -> None:
    client = configured_client()
    first = client.post(
        "/api/v1/siniestros/42/relaciones/detectar",
        json=PAYLOAD,
        headers=HEADERS,
    )
    repeated = client.post(
        "/api/v1/siniestros/42/relaciones/detectar",
        json=PAYLOAD,
        headers=HEADERS,
    )
    assert repeated.json() == first.json()


def test_operator_cannot_detect_relations() -> None:
    response = configured_client(PrincipalRole.OPERADOR).post(
        "/api/v1/siniestros/42/relaciones/detectar",
        json=PAYLOAD,
        headers=HEADERS,
    )
    assert response.status_code == 403
    assert response.json()["codigo"] == "CASE-RELATION-FORBIDDEN"
