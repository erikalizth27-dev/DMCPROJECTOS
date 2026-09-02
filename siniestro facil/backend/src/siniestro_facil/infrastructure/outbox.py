from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True, slots=True)
class OutboxEvent:
    event_id: str
    event_type: str
    aggregate_id: str
    occurred_at: datetime
    payload: dict[str, object]


class EventTransport(Protocol):
    def publish(self, event: OutboxEvent) -> None: ...


class InMemoryIdempotentTransport:
    """Transporte de prueba; no representa una integración Pub/Sub."""

    def __init__(self) -> None:
        self._published: dict[str, OutboxEvent] = {}

    def publish(self, event: OutboxEvent) -> None:
        previous = self._published.get(event.event_id)
        if previous is not None and previous != event:
            raise ValueError(
                "El identificador del evento ya fue usado con otro contenido"
            )
        self._published[event.event_id] = event

    @property
    def events(self) -> tuple[OutboxEvent, ...]:
        return tuple(self._published.values())
