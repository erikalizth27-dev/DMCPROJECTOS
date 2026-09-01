from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from siniestro_facil.api.routes.claims import (
    get_authenticated_principal,
    get_register_evidence_service,
)
from siniestro_facil.application.register_evidence import (
    RegisterEvidenceService,
    RegisteredEvidence,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import (
    ActorType,
    AuthenticatedPrincipal,
)
from siniestro_facil.infrastructure.evidence_storage import APPROVED_BUCKET
from siniestro_facil.main import create_app


DIGEST = "a" * 64
URI = (
    f"gs://{APPROVED_BUCKET}/"
    "siniestros/42/originales/evidencia-sintetica.jpg"
)


class ApiEvidenceRepository:
    def find_request(self, idempotency_key, principal):
        del idempotency_key, principal
        return None

    def create(
        self,
        command,
        principal,
        *,
        idempotency_key,
        fingerprint,
    ):
        del principal, idempotency_key, fingerprint
        return RegisteredEvidence(
            id=7,
            claim_id=command.claim_id,
            evidence_type=command.evidence_type,
            original_uri=command.original_uri,
            sha256_hex=command.sha256_hex,
            received_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
            derived_from_id=command.derived_from_id,
        )


def principal() -> AuthenticatedPrincipal:
    now = datetime.now(timezone.utc)
    return AuthenticatedPrincipal(
        subject="insured-synthetic",
        role=PrincipalRole.ASEGURADO,
        actor_type=ActorType.EXTERNO,
        tenant_id="tenant-synthetic",
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


def client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_authenticated_principal] = principal
    app.dependency_overrides[get_register_evidence_service] = (
        lambda: RegisterEvidenceService(ApiEvidenceRepository())
    )
    return TestClient(app)


def payload():
    return {
        "tipoEvidencia": "fotografia",
        "contenidoOriginalUri": URI,
        "hash": DIGEST,
        "fuente": "asegurado",
        "metadatos": {"generation": "1"},
    }


def test_registers_evidence_with_http_201() -> None:
    response = client().post(
        "/api/v1/siniestros/42/evidencias",
        json=payload(),
        headers={"Idempotency-Key": "evidence-idem-0001"},
    )
    assert response.status_code == 201
    assert response.json()["id"] == 7
    assert response.json()["siniestroId"] == 42
    assert response.json()["hash"] == DIGEST


def test_requires_idempotency_header() -> None:
    response = client().post(
        "/api/v1/siniestros/42/evidencias",
        json=payload(),
    )
    assert response.status_code == 422


def test_rejects_non_cloud_storage_uri() -> None:
    response = client().post(
        "/api/v1/siniestros/42/evidencias",
        json={
            **payload(),
            "contenidoOriginalUri": "https://example.invalid/file.jpg",
        },
        headers={"Idempotency-Key": "evidence-idem-0001"},
    )
    assert response.status_code == 422


def test_requires_authentication_by_default() -> None:
    app = create_app()
    app.dependency_overrides[get_register_evidence_service] = (
        lambda: RegisterEvidenceService(ApiEvidenceRepository())
    )
    response = TestClient(app).post(
        "/api/v1/siniestros/42/evidencias",
        json=payload(),
        headers={"Idempotency-Key": "evidence-idem-0001"},
    )
    assert response.status_code == 401
    assert response.json()["codigo"] == "AUTHENTICATION-REQUIRED"
