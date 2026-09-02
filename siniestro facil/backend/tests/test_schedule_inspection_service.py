from datetime import datetime, timedelta, timezone

import pytest

from siniestro_facil.application.schedule_inspection import (
    GetInspectionService,
    InMemoryInspectionSchedulingRepository,
    InspectionSchedulingError,
    ScheduleInspectionCommand,
    ScheduleInspectionService,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal


def principal(role: PrincipalRole = PrincipalRole.OPERADOR) -> AuthenticatedPrincipal:
    now = datetime.now(timezone.utc)
    return AuthenticatedPrincipal(
        subject=f"{role.value}-synthetic",
        role=role,
        actor_type=ActorType.INTERNO,
        tenant_id="tenant-synthetic",
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


def command() -> ScheduleInspectionCommand:
    return ScheduleInspectionCommand(
        claim_id=42,
        scheduled_at=datetime.now(timezone.utc) + timedelta(days=1),
        expected_version=3,
        reason="Programación requerida",
    )


@pytest.mark.parametrize(
    "role",
    [PrincipalRole.OPERADOR, PrincipalRole.AJUSTADOR],
)
def test_authorized_roles_schedule_inspection(role: PrincipalRole) -> None:
    result = ScheduleInspectionService(
        InMemoryInspectionSchedulingRepository()
    ).execute(command(), principal(role))

    assert result.claim_id == 42
    assert result.current_state.value == "inspeccion_programada"
    assert result.version == 4


def test_rejects_unauthorized_role() -> None:
    with pytest.raises(InspectionSchedulingError) as caught:
        ScheduleInspectionService(
            InMemoryInspectionSchedulingRepository()
        ).execute(command(), principal(PrincipalRole.TALLER))

    assert caught.value.code == "INSPECTION-FORBIDDEN"
    assert caught.value.status_code == 403


def test_requires_reason() -> None:
    invalid = ScheduleInspectionCommand(
        claim_id=42,
        scheduled_at=command().scheduled_at,
        expected_version=3,
        reason=" ",
    )

    with pytest.raises(InspectionSchedulingError) as caught:
        ScheduleInspectionService(
            InMemoryInspectionSchedulingRepository()
        ).execute(invalid, principal())

    assert caught.value.code == "INSPECTION-REASON-REQUIRED"


def test_requires_timezone() -> None:
    invalid = ScheduleInspectionCommand(
        claim_id=42,
        scheduled_at=datetime(2026, 9, 3, 10, 0),
        expected_version=3,
        reason="Programación",
    )

    with pytest.raises(InspectionSchedulingError) as caught:
        ScheduleInspectionService(
            InMemoryInspectionSchedulingRepository()
        ).execute(invalid, principal())

    assert caught.value.code == "INSPECTION-DATETIME-INVALID"


def test_get_hides_missing_or_unrelated_inspection() -> None:
    repository = InMemoryInspectionSchedulingRepository()
    scheduled = ScheduleInspectionService(repository).execute(
        command(),
        principal(),
    )
    service = GetInspectionService(repository)

    assert service.execute(42, scheduled.id, principal()) == scheduled
    with pytest.raises(InspectionSchedulingError) as caught:
        service.execute(99, scheduled.id, principal())

    assert caught.value.code == "INSPECTION-NOT-FOUND"
