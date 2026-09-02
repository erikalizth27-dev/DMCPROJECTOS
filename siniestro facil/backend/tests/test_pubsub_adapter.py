from datetime import datetime, timezone

import pytest

from siniestro_facil.infrastructure.pubsub_adapter import (
    IdempotentMessageConsumer,
    InMemoryPubSubTransport,
    PubSubEnvelope,
    PubSubMessageConflict,
)


def message(**payload: object) -> PubSubEnvelope:
    return PubSubEnvelope(
        event_id="assistance-event-0001",
        event_type="assistance.retry.requested",
        ordering_key="claim-42",
        occurred_at=datetime(2026, 9, 2, tzinfo=timezone.utc),
        payload={"assistance_id": 10, **payload},
    )


def test_publishes_same_message_idempotently() -> None:
    transport = InMemoryPubSubTransport()
    transport.publish(message())
    transport.publish(message())
    assert len(transport.published) == 1


def test_rejects_same_event_id_with_other_content() -> None:
    transport = InMemoryPubSubTransport()
    transport.publish(message())
    with pytest.raises(PubSubMessageConflict):
        transport.publish(message(attempt=2))


def test_consumer_executes_handler_once() -> None:
    consumer = IdempotentMessageConsumer()
    calls = 0

    def handler(event: PubSubEnvelope) -> str:
        nonlocal calls
        calls += 1
        return event.event_id

    first = consumer.consume(message(), handler)
    second = consumer.consume(message(), handler)
    assert first == second
    assert calls == 1


def test_consumer_rejects_changed_redelivery() -> None:
    consumer = IdempotentMessageConsumer()
    consumer.consume(message(), lambda event: event.event_id)
    with pytest.raises(PubSubMessageConflict):
        consumer.consume(
            message(attempt=2),
            lambda event: event.event_id,
        )


def test_dead_letter_is_idempotent_and_requires_reason() -> None:
    transport = InMemoryPubSubTransport()
    event = message()
    transport.dead_letter(event, reason="fallo permanente")
    transport.dead_letter(event, reason="fallo permanente")
    assert len(transport.dead_letters) == 1
    with pytest.raises(ValueError):
        transport.dead_letter(message(event="other"), reason=" ")
