from datetime import datetime, timedelta, timezone

import pytest

from siniestro_facil.application.assistance_contracts import AssistanceRecord
from siniestro_facil.application.manage_assistance import (
    AssistanceManagementError,
    InMemoryAssistanceManagementRepository,
    ReassignAssistanceCommand,
    ReassignAssistanceService,
    RegisterProviderReplyCommand,
    RegisterProviderReplyService,
)
from siniestro_facil.domain.assistance import (
    AssistanceStatus,
    ProviderResult,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import (
    ActorType,
    AuthenticatedPrincipal,
)


def principal(
    role: PrincipalRole = PrincipalRole.OPERADOR,
) -> AuthenticatedPrincipal:
    now = datetime.now(timezone.utc)
    return AuthenticatedPrincipal(
        subject="operator-s3-be-02",
        role=role,
        actor_type=ActorType.INTERNO,
        tenant_id="tenant-synthetic",
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


def record(
    *,
    status: AssistanceStatus = AssistanceStatus.SENT,
    attempt: int = 1,
) -> AssistanceRecord:
    now = datetime.now(timezone.utc)
    return AssistanceRecord(
        id=10,
        claim_id=42,
        provider_id=7,
        assistance_type="grua",
        status=status,
        attempt=attempt,
        created_at=now,
        updated_at=now,
    )


def repository(
    current: AssistanceRecord,
) -> InMemoryAssistanceManagementRepository:
    return InMemoryAssistanceManagementRepository(
        [current],
        visible_claim_ids={42},
    )


@pytest.mark.parametrize(
    ("result", "expected"),
    [
        (ProviderResult.ACCEPTED, AssistanceStatus.ACCEPTED),
        (ProviderResult.REJECTED, AssistanceStatus.REJECTED),
        (ProviderResult.NO_RESPONSE, AssistanceStatus.NO_RESPONSE),
    ],
)
def test_registers_provider_result(
    result: ProviderResult,
    expected: AssistanceStatus,
) -> None:
    service = RegisterProviderReplyService(repository(record()))
    updated = service.execute(
        RegisterProviderReplyCommand(42, 10, result, 1),
        principal(),
    )
    assert updated.status is expected
    assert updated.attempt == 1


def test_rejects_stale_attempt() -> None:
    service = RegisterProviderReplyService(
        repository(record(attempt=2))
    )
    with pytest.raises(AssistanceManagementError) as error:
        service.execute(
            RegisterProviderReplyCommand(
                42,
                10,
                ProviderResult.ACCEPTED,
                1,
            ),
            principal(),
        )
    assert error.value.code == "ASSISTANCE-VERSION-CONFLICT"
    assert error.value.status_code == 409


def test_rejects_second_terminal_reply() -> None:
    service = RegisterProviderReplyService(
        repository(record(status=AssistanceStatus.ACCEPTED))
    )
    with pytest.raises(AssistanceManagementError) as error:
        service.execute(
            RegisterProviderReplyCommand(
                42,
                10,
                ProviderResult.REJECTED,
                1,
            ),
            principal(),
        )
    assert error.value.code == "ASSISTANCE-TRANSITION-INVALID"


def test_reassigns_after_no_response_and_preserves_history() -> None:
    storage = repository(
        record(status=AssistanceStatus.NO_RESPONSE)
    )
    service = ReassignAssistanceService(storage)
    replacement = service.execute(
        ReassignAssistanceCommand(
            claim_id=42,
            assistance_id=10,
            new_provider_id=8,
            expected_attempt=1,
            reason="Proveedor sin respuesta",
        ),
        principal(),
    )
    assert replacement.id != 10
    assert replacement.provider_id == 8
    assert replacement.attempt == 2
    assert replacement.status is AssistanceStatus.PENDING


def test_rejects_same_provider() -> None:
    service = ReassignAssistanceService(
        repository(record(status=AssistanceStatus.REJECTED))
    )
    with pytest.raises(AssistanceManagementError) as error:
        service.execute(
            ReassignAssistanceCommand(
                42,
                10,
                7,
                1,
                "Proveedor rechazó",
            ),
            principal(),
        )
    assert error.value.code == "PROVIDER-INVALID"


def test_rejects_reassignment_before_provider_result() -> None:
    service = ReassignAssistanceService(repository(record()))
    with pytest.raises(AssistanceManagementError) as error:
        service.execute(
            ReassignAssistanceCommand(
                42,
                10,
                8,
                1,
                "Cambio prematuro",
            ),
            principal(),
        )
    assert error.value.code == "ASSISTANCE-REASSIGNMENT-INVALID"


def test_stops_after_third_attempt() -> None:
    service = ReassignAssistanceService(
        repository(
            record(
                status=AssistanceStatus.NO_RESPONSE,
                attempt=3,
            )
        )
    )
    with pytest.raises(AssistanceManagementError) as error:
        service.execute(
            ReassignAssistanceCommand(
                42,
                10,
                8,
                3,
                "Tercer fallo",
            ),
            principal(),
        )
    assert error.value.code == "RETRY-LIMIT-REACHED"


def test_denies_unauthorized_role() -> None:
    service = RegisterProviderReplyService(repository(record()))
    with pytest.raises(AssistanceManagementError) as error:
        service.execute(
            RegisterProviderReplyCommand(
                42,
                10,
                ProviderResult.ACCEPTED,
                1,
            ),
            principal(PrincipalRole.TALLER),
        )
    assert error.value.status_code == 403
