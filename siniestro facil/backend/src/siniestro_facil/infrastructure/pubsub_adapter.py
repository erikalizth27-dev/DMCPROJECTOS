from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Protocol


class PubSubMessageConflict(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class PubSubEnvelope:
    event_id: str
    event_type: str
    ordering_key: str
    occurred_at: datetime
    payload: dict[str, object]

    @property
    def fingerprint(self) -> str:
        canonical = json.dumps(
            {
                "event_id": self.event_id,
                "event_type": self.event_type,
                "ordering_key": self.ordering_key,
                "occurred_at": self.occurred_at.isoformat(),
                "payload": self.payload,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class PubSubTransport(Protocol):
    def publish(self, message: PubSubEnvelope) -> str: ...

    def dead_letter(
        self,
        message: PubSubEnvelope,
        *,
        reason: str,
    ) -> None: ...


class InMemoryPubSubTransport:
    """Doble de prueba; no crea ni utiliza recursos GCP."""

    def __init__(self) -> None:
        self._published: dict[str, PubSubEnvelope] = {}
        self._dead_letters: dict[str, tuple[PubSubEnvelope, str]] = {}

    def publish(self, message: PubSubEnvelope) -> str:
        previous = self._published.get(message.event_id)
        if previous is not None and previous != message:
            raise PubSubMessageConflict(
                "event_id ya fue utilizado con otro contenido"
            )
        self._published[message.event_id] = message
        return message.event_id

    def dead_letter(
        self,
        message: PubSubEnvelope,
        *,
        reason: str,
    ) -> None:
        normalized = reason.strip()
        if not normalized:
            raise ValueError("Dead letter requiere una razón")
        previous = self._dead_letters.get(message.event_id)
        value = (message, normalized)
        if previous is not None and previous != value:
            raise PubSubMessageConflict(
                "event_id ya fue enviado a dead letter con otro contenido"
            )
        self._dead_letters[message.event_id] = value

    @property
    def published(self) -> tuple[PubSubEnvelope, ...]:
        return tuple(self._published.values())

    @property
    def dead_letters(
        self,
    ) -> tuple[tuple[PubSubEnvelope, str], ...]:
        return tuple(self._dead_letters.values())


class IdempotentMessageConsumer:
    def __init__(self) -> None:
        self._processed: dict[str, tuple[str, object]] = {}

    def consume(
        self,
        message: PubSubEnvelope,
        handler: Callable[[PubSubEnvelope], object],
    ) -> object:
        previous = self._processed.get(message.event_id)
        if previous is not None:
            fingerprint, result = previous
            if fingerprint != message.fingerprint:
                raise PubSubMessageConflict(
                    "event_id recibido nuevamente con otro contenido"
                )
            return result
        result = handler(message)
        self._processed[message.event_id] = (
            message.fingerprint,
            result,
        )
        return result
