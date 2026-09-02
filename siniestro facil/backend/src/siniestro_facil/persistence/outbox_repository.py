from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from siniestro_facil.persistence.models import EventoOutbox


@dataclass(frozen=True, slots=True)
class OutboxRecord:
    event_id: str
    aggregate_type: str
    aggregate_id: int
    event_type: str
    payload: dict[str, object]
    attempts: int
    occurred_at: datetime
    available_at: datetime


class PostgreSQLOutboxRepository:
    """Outbox con reclamación SKIP LOCKED para publicación concurrente segura."""

    def __init__(self, factory: sessionmaker[Session]) -> None:
        self._factory = factory

    @staticmethod
    def enqueue(
        session: Session,
        *,
        event_id: str,
        aggregate_type: str,
        aggregate_id: int,
        event_type: str,
        payload: dict[str, object],
        occurred_at: datetime,
        available_at: datetime | None = None,
    ) -> EventoOutbox:
        row = EventoOutbox(
            event_id=event_id,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            event_type=event_type,
            payload=payload,
            estado="pendiente",
            intentos=0,
            ocurrido_en=occurred_at,
            disponible_en=available_at or occurred_at,
        )
        session.add(row)
        return row

    @staticmethod
    def _record(row: EventoOutbox) -> OutboxRecord:
        return OutboxRecord(
            event_id=row.event_id,
            aggregate_type=row.aggregate_type,
            aggregate_id=row.aggregate_id,
            event_type=row.event_type,
            payload=row.payload,
            attempts=row.intentos,
            occurred_at=row.ocurrido_en,
            available_at=row.disponible_en,
        )

    def claim_batch(self, *, limit: int = 100) -> tuple[OutboxRecord, ...]:
        if not 1 <= limit <= 500:
            raise ValueError("limit debe estar entre 1 y 500")
        now = datetime.now(timezone.utc)
        with self._factory() as session, session.begin():
            rows = tuple(
                session.scalars(
                    select(EventoOutbox)
                    .where(
                        EventoOutbox.estado.in_(("pendiente", "fallido")),
                        EventoOutbox.disponible_en <= now,
                    )
                    .order_by(
                        EventoOutbox.disponible_en,
                        EventoOutbox.id_evento_outbox,
                    )
                    .limit(limit)
                    .with_for_update(skip_locked=True)
                )
            )
            for row in rows:
                row.estado = "publicando"
                row.intentos += 1
                row.ultimo_error = None
            return tuple(self._record(row) for row in rows)

    def mark_published(
        self,
        event_id: str,
        pubsub_message_id: str,
    ) -> None:
        message_id = pubsub_message_id.strip()
        if not message_id:
            raise ValueError("pubsub_message_id es obligatorio")
        with self._factory() as session, session.begin():
            row = session.scalar(
                select(EventoOutbox)
                .where(EventoOutbox.event_id == event_id)
                .with_for_update()
            )
            if row is None:
                raise LookupError("Evento outbox no encontrado")
            if row.estado == "publicado":
                if row.pubsub_message_id != message_id:
                    raise ValueError(
                        "El evento ya fue publicado con otro message_id"
                    )
                return
            if row.estado != "publicando":
                raise ValueError("El evento no está reclamado para publicación")
            row.estado = "publicado"
            row.publicado_en = datetime.now(timezone.utc)
            row.pubsub_message_id = message_id
            row.ultimo_error = None

    def mark_failed(self, event_id: str, error: str) -> None:
        normalized = error.strip()
        if not normalized:
            raise ValueError("El error es obligatorio")
        with self._factory() as session, session.begin():
            row = session.scalar(
                select(EventoOutbox)
                .where(EventoOutbox.event_id == event_id)
                .with_for_update()
            )
            if row is None:
                raise LookupError("Evento outbox no encontrado")
            if row.estado == "publicado":
                raise ValueError("Un evento publicado no puede marcarse fallido")
            row.estado = "fallido"
            row.ultimo_error = normalized[:2000]
