from datetime import datetime, timezone

import pytest

from siniestro_facil.application.assistance_contracts import AssistanceRecord
from siniestro_facil.domain.assistance import (
    AssistanceStatus,
    InvalidAssistanceTransition,
    RetryPolicy,
    validate_assistance_transition,
)
from siniestro_facil.infrastructure.outbox import (
    InMemoryIdempotentTransport,
    OutboxEvent,
)
from siniestro_facil.infrastructure.provider_adapter import (
    DisabledProviderAdapter,
    ProviderIntegrationDisabled,
    dispatch_assistance,
)


def test_allows_request_to_be_sent() -> None:
    validate_assistance_transition(
        AssistanceStatus.PENDING,
        AssistanceStatus.SENT,
    )


def test_allows_retry_after_no_response() -> None:
    validate_assistance_transition(
        AssistanceStatus.NO_RESPONSE,
        AssistanceStatus.SENT,
    )


def test_rejects_change_after_acceptance() -> None:
    with pytest.raises(InvalidAssistanceTransition):
        validate_assistance_transition(
            AssistanceStatus.ACCEPTED,
            AssistanceStatus.SENT,
        )


def test_retry_policy_has_no_implicit_defaults() -> None:
    policy = RetryPolicy((30, 120, 300), timeout_seconds=10)
    assert policy.max_attempts == 3


@pytest.mark.parametrize(
    ("delays", "timeout"),
    [
        ((), 10),
        ((0,), 10),
        ((10,), 0),
    ],
)
def test_retry_policy_rejects_invalid_values(
    delays: tuple[int, ...],
    timeout: int,
) -> None:
    with pytest.raises(ValueError):
        RetryPolicy(delays, timeout_seconds=timeout)


def test_provider_is_disabled_before_decision() -> None:
    now = datetime.now(timezone.utc)
    assistance = AssistanceRecord(
        id=1,
        claim_id=2,
        provider_id=3,
        assistance_type="grua",
        status=AssistanceStatus.PENDING,
        attempt=1,
        created_at=now,
        updated_at=now,
    )
    with pytest.raises(ProviderIntegrationDisabled):
        dispatch_assistance(
            DisabledProviderAdapter(),
            assistance,
            idempotency_key="assistance-idempotency-0001",
        )


def test_outbox_transport_is_idempotent() -> None:
    event = OutboxEvent(
        event_id="event-0001",
        event_type="assistance.requested",
        aggregate_id="10",
        occurred_at=datetime.now(timezone.utc),
        payload={"provider_id": 3},
    )
    transport = InMemoryIdempotentTransport()
    transport.publish(event)
    transport.publish(event)
    assert transport.events == (event,)


def test_outbox_rejects_reused_id_with_other_content() -> None:
    now = datetime.now(timezone.utc)
    first = OutboxEvent("event-0001", "a", "10", now, {"value": 1})
    second = OutboxEvent("event-0001", "a", "10", now, {"value": 2})
    transport = InMemoryIdempotentTransport()
    transport.publish(first)
    with pytest.raises(ValueError):
        transport.publish(second)
