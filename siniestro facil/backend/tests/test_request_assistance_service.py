from datetime import datetime, timedelta, timezone

import pytest

from siniestro_facil.application.request_assistance import (
    AssistanceRequestError,
    GetAssistanceService,
    InMemoryAssistanceRepository,
    RequestAssistanceCommand,
    RequestAssistanceService,
)
from siniestro_facil.domain.assistance import AssistanceStatus
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import (
    ActorType,
    AuthenticatedPrincipal,
)
from siniestro_facil.infrastructure.provider_adapter import (
    SimulatedProviderAdapter,
)


def principal(
    role: PrincipalRole = PrincipalRole.OPERADOR,
) -> AuthenticatedPrincipal:
    now = datetime.now(timezone.utc)
    return AuthenticatedPrincipal(
        subject="actor-sprint-3",
        role=role,
        actor_type=ActorType.INTERNO,
        tenant_id="tenant-synthetic",
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


def command(**changes: object) -> RequestAssistanceCommand:
    values: dict[str, object] = {
        "claim_id": 42,
        "provider_id": 7,
        "assistance_type": "grua",
        "reason": "Vehículo inmovilizado",
    }
    values.update(changes)
    return RequestAssistanceCommand(**values)  # type: ignore[arg-type]


def payload(**changes: object) -> dict[str, object]:
    values: dict[str, object] = {
        "providerId": 7,
        "tipoAsistencia": "grua",
        "motivo": "Vehículo inmovilizado",
    }
    values.update(changes)
    return values


def services() -> tuple[
    RequestAssistanceService,
    GetAssistanceService,
    SimulatedProviderAdapter,
]:
    repository = InMemoryAssistanceRepository(visible_claim_ids={42})
    provider = SimulatedProviderAdapter()
    return (
        RequestAssistanceService(repository, provider),
        GetAssistanceService(repository),
        provider,
    )


def test_requests_assistance_and_dispatches_provider() -> None:
    request_service, _, provider = services()
    result = request_service.execute(
        command(),
        principal(),
        idempotency_key="assistance-idem-0001",
        request_payload=payload(),
    )
    assert result.status is AssistanceStatus.SENT
    assert result.attempt == 1
    assert len(provider.dispatches) == 1


def test_replays_same_request_without_second_dispatch() -> None:
    request_service, _, provider = services()
    first = request_service.execute(
        command(),
        principal(),
        idempotency_key="assistance-idem-0001",
        request_payload=payload(),
    )
    second = request_service.execute(
        command(),
        principal(),
        idempotency_key="assistance-idem-0001",
        request_payload=payload(),
    )
    assert second == first
    assert len(provider.dispatches) == 1


def test_rejects_same_key_with_other_payload() -> None:
    request_service, _, _ = services()
    request_service.execute(
        command(),
        principal(),
        idempotency_key="assistance-idem-0001",
        request_payload=payload(),
    )
    with pytest.raises(AssistanceRequestError) as error:
        request_service.execute(
            command(reason="Otro motivo"),
            principal(),
            idempotency_key="assistance-idem-0001",
            request_payload=payload(motivo="Otro motivo"),
        )
    assert error.value.code == "IDEMPOTENCY-CONFLICT"
    assert error.value.status_code == 409


def test_hides_claim_outside_scope() -> None:
    repository = InMemoryAssistanceRepository(visible_claim_ids={99})
    service = RequestAssistanceService(
        repository,
        SimulatedProviderAdapter(),
    )
    with pytest.raises(AssistanceRequestError) as error:
        service.execute(
            command(),
            principal(),
            idempotency_key="assistance-idem-0001",
            request_payload=payload(),
        )
    assert error.value.code == "CLAIM-NOT-FOUND"


def test_denies_role_without_permission() -> None:
    request_service, _, _ = services()
    with pytest.raises(AssistanceRequestError) as error:
        request_service.execute(
            command(),
            principal(PrincipalRole.TALLER),
            idempotency_key="assistance-idem-0001",
            request_payload=payload(),
        )
    assert error.value.status_code == 403


@pytest.mark.parametrize(
    "invalid",
    [
        {"provider_id": 0},
        {"assistance_type": " "},
        {"reason": " "},
    ],
)
def test_rejects_invalid_request(invalid: dict[str, object]) -> None:
    request_service, _, _ = services()
    with pytest.raises(AssistanceRequestError) as error:
        request_service.execute(
            command(**invalid),
            principal(),
            idempotency_key="assistance-idem-0001",
            request_payload=payload(),
        )
    assert error.value.status_code == 422


def test_consults_created_assistance() -> None:
    request_service, get_service, _ = services()
    created = request_service.execute(
        command(),
        principal(),
        idempotency_key="assistance-idem-0001",
        request_payload=payload(),
    )
    result = get_service.execute(42, created.id, principal())
    assert result == created


def test_hides_missing_assistance() -> None:
    _, get_service, _ = services()
    with pytest.raises(AssistanceRequestError) as error:
        get_service.execute(42, 999, principal())
    assert error.value.code == "ASSISTANCE-NOT-FOUND"
    assert error.value.status_code == 404
