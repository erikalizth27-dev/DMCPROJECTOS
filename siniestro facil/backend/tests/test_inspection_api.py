from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from siniestro_facil.api.routes.claims import get_authenticated_principal
from siniestro_facil.api.routes.inspections import (
    get_get_inspection_service,
    get_schedule_inspection_service,
)
from siniestro_facil.application.schedule_inspection import (
    GetInspectionService,
    InMemoryInspectionSchedulingRepository,
    ScheduleInspectionService,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal
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


def configured_client() -> TestClient:
    repository = InMemoryInspectionSchedulingRepository()
    app = create_app()
    app.dependency_overrides[get_authenticated_principal] = principal
    app.dependency_overrides[get_schedule_inspection_service] = (
        lambda: ScheduleInspectionService(repository)
    )
    app.dependency_overrides[get_get_inspection_service] = (
        lambda: GetInspectionService(repository)
    )
    return TestClient(app)


def test_schedules_and_gets_inspection() -> None:
    client = configured_client()
    scheduled_at = datetime.now(timezone.utc) + timedelta(days=1)

    created = client.post(
        "/api/v1/siniestros/42/inspecciones",
        json={
            "fechaProgramada": scheduled_at.isoformat(),
            "version": 3,
            "motivo": "Programación requerida",
        },
    )

    assert created.status_code == 201
    body = created.json()
    assert body["siniestroId"] == 42
    assert body["estadoActual"] == "inspeccion_programada"
    assert body["version"] == 4

    found = client.get(
        f"/api/v1/siniestros/42/inspecciones/{body['id']}"
    )
    assert found.status_code == 200
    assert found.json() == body


def test_hides_unrelated_inspection() -> None:
    client = configured_client()
    created = client.post(
        "/api/v1/siniestros/42/inspecciones",
        json={
            "fechaProgramada": (
                datetime.now(timezone.utc) + timedelta(days=1)
            ).isoformat(),
            "version": 0,
            "motivo": "Programación",
        },
    )

    response = client.get(
        f"/api/v1/siniestros/99/inspecciones/{created.json()['id']}"
    )

    assert response.status_code == 404
    assert response.json()["codigo"] == "INSPECTION-NOT-FOUND"


def test_rejects_datetime_without_timezone() -> None:
    response = configured_client().post(
        "/api/v1/siniestros/42/inspecciones",
        json={
            "fechaProgramada": "2026-09-03T10:00:00",
            "version": 0,
            "motivo": "Programación",
        },
    )

    assert response.status_code == 422
    assert response.json()["codigo"] == "INSPECTION-DATETIME-INVALID"


def test_requires_authentication_by_default() -> None:
    response = TestClient(create_app()).post(
        "/api/v1/siniestros/42/inspecciones",
        json={
            "fechaProgramada": "2026-09-03T10:00:00Z",
            "version": 0,
            "motivo": "Programación",
        },
    )

    assert response.status_code == 401
