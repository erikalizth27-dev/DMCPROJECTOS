from __future__ import annotations

from dataclasses import dataclass

from siniestro_facil.infrastructure.pubsub_adapter import (
    PubSubEnvelope,
    PubSubTransport,
)
from siniestro_facil.persistence.outbox_repository import (
    OutboxRecord,
    PostgreSQLOutboxRepository,
)


@dataclass(frozen=True, slots=True)
class OutboxPublishResult:
    published: int
    failed: int


class PublishAssistanceOutbox:
    def __init__(
        self,
        repository: PostgreSQLOutboxRepository,
        transport: PubSubTransport,
    ) -> None:
        self._repository = repository
        self._transport = transport

    @staticmethod
    def _envelope(record: OutboxRecord) -> PubSubEnvelope:
        return PubSubEnvelope(
            event_id=record.event_id,
            event_type=record.event_type,
            ordering_key=(
                f"{record.aggregate_type}:{record.aggregate_id}"
            ),
            occurred_at=record.occurred_at,
            payload=record.payload,
        )

    def run(self, *, limit: int = 100) -> OutboxPublishResult:
        published = 0
        failed = 0
        for record in self._repository.claim_batch(limit=limit):
            message = self._envelope(record)
            try:
                message_id = self._transport.publish(message)
                self._repository.mark_published(
                    record.event_id,
                    message_id,
                )
                published += 1
            except Exception as exc:
                self._repository.mark_failed(
                    record.event_id,
                    f"{type(exc).__name__}: {exc}",
                )
                failed += 1
        return OutboxPublishResult(published=published, failed=failed)
