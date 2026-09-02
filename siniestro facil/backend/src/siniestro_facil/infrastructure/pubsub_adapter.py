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


class GooglePubSubTransport:
    """Adaptador real con cliente inyectable para pruebas sin credenciales."""

    def __init__(
        self,
        *,
        project_id: str,
        topic_id: str,
        dead_letter_topic_id: str,
        client: object | None = None,
        publish_timeout_seconds: int = 10,
    ) -> None:
        if client is None:
            from google.cloud import pubsub_v1

            client = pubsub_v1.PublisherClient(
                publisher_options=pubsub_v1.types.PublisherOptions(
                    enable_message_ordering=True
                )
            )
        self._client = client
        self._topic_path = client.topic_path(project_id, topic_id)
        self._dead_letter_topic_path = client.topic_path(
            project_id,
            dead_letter_topic_id,
        )
        self._publish_timeout_seconds = publish_timeout_seconds

    @staticmethod
    def _data(message: PubSubEnvelope) -> bytes:
        return json.dumps(
            {
                "event_id": message.event_id,
                "event_type": message.event_type,
                "ordering_key": message.ordering_key,
                "occurred_at": message.occurred_at.isoformat(),
                "payload": message.payload,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")

    def _publish(
        self,
        topic_path: str,
        message: PubSubEnvelope,
        **extra_attributes: str,
    ) -> str:
        future = self._client.publish(
            topic_path,
            self._data(message),
            ordering_key=message.ordering_key,
            event_id=message.event_id,
            event_type=message.event_type,
            **extra_attributes,
        )
        return str(future.result(timeout=self._publish_timeout_seconds))

    def publish(self, message: PubSubEnvelope) -> str:
        return self._publish(self._topic_path, message)

    def dead_letter(
        self,
        message: PubSubEnvelope,
        *,
        reason: str,
    ) -> None:
        normalized = reason.strip()
        if not normalized:
            raise ValueError("Dead letter requiere una razón")
        self._publish(
            self._dead_letter_topic_path,
            message,
            dead_letter_reason=normalized,
        )
