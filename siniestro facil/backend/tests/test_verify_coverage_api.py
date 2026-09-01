from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from fastapi.testclient import TestClient

from siniestro_facil.api.routes.claims import (
    get_authenticated_principal,
    get_verify_coverage_service,
)
from siniestro_facil.application.verify_coverage import (
    CoverageContext,
    InMemoryCoverageRepository,
    VerifyCoverageService,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.enums import EstadoSiniestro
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal
from siniestro_facil.infrastructure.policy_adapter import (
    InMemoryPolicyAdapter,
    PolicySnapshot,
)
from siniestro_facil.main import create_app


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


def service(*, version: int = 0) -> VerifyCoverageService:
    policy = PolicySnapshot(
        numero_poliza="POL-SYN-001",
        numero_documento="DOC-SYN-001",
        placa="SYN0001",
        vigente_desde=date(2026, 1, 1),
        vigente_hasta=date(2026, 12, 31),
        deducible=Decimal("500.00"),
    )
    context = CoverageContext(
        claim_id=42,
        policy_number=policy.numero_poliza,
        document_number=policy.numero_documento,
        plate=policy.placa,
        event_date=date(2026, 8, 28),
        current_state=EstadoSiniestro.REPORTADO,
        version=version,
    )
    return VerifyCoverageService(
        InMemoryPolicyAdapter([policy]),
        InMemoryCoverageRepository([context]),
    )


def client(*, version: int = 0) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_authenticated_principal] = principal
    app.dependency_overrides[get_verify_coverage_service] = (
        lambda: service(version=version)
    )
    return TestClient(app)


def test_verifies_coverage_with_http_200() -> None:
    response = client().post(
        "/api/v1/siniestros/42/cobertura/verificacion",
        json={"version": 0},
    )
    assert response.status_code == 200
    assert response.json() == {
        "siniestroId": 42,
        "coberturaActiva": True,
        "deducible": "500.00",
        "estadoValidacion": "activa",
        "estadoActual": "validando_cobertura",
        "version": 1,
        "requiereRevisionHumana": False,
    }


def test_returns_http_409_for_stale_version() -> None:
    response = client(version=2).post(
        "/api/v1/siniestros/42/cobertura/verificacion",
        json={"version": 1},
    )
    assert response.status_code == 409
    assert response.json()["codigo"] == "STATE-VERSION-CONFLICT"
    assert response.json()["detalles"] == []


def test_requires_nonnegative_version() -> None:
    response = client().post(
        "/api/v1/siniestros/42/cobertura/verificacion",
        json={"version": -1},
    )
    assert response.status_code == 422


def test_requires_authentication_by_default() -> None:
    app = create_app()
    app.dependency_overrides[get_verify_coverage_service] = service
    response = TestClient(app).post(
        "/api/v1/siniestros/42/cobertura/verificacion",
        json={"version": 0},
    )
    assert response.status_code == 401
    assert response.json()["codigo"] == "AUTHENTICATION-REQUIRED"
