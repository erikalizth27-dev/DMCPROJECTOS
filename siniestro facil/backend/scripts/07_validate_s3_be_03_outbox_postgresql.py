from __future__ import annotations

import os
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from siniestro_facil.persistence.models import EventoOutbox
from siniestro_facil.persistence.outbox_repository import (
    PostgreSQLOutboxRepository,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL no configurada")

engine = create_engine(database_url, pool_pre_ping=True)
event_id = str(uuid4())
message_id = f"pubsub-synthetic-{uuid4()}"
connection = engine.connect()
outer_transaction = connection.begin()
factory = sessionmaker(
    bind=connection,
    class_=Session,
    expire_on_commit=False,
)
repository = PostgreSQLOutboxRepository(factory)

try:
    now = datetime.now(timezone.utc)
    with factory() as session, session.begin():
        PostgreSQLOutboxRepository.enqueue(
            session,
            event_id=event_id,
            aggregate_type="asistencia",
            aggregate_id=999999999,
            event_type="asistencia.reintento_solicitado",
            payload={
                "id_asistencia": 999999999,
                "numero_intento": 2,
                "delay_seconds": 30,
            },
            occurred_at=now,
        )

    claimed = repository.claim_batch(limit=100)
    matching = tuple(
        record for record in claimed if record.event_id == event_id
    )
    require(len(matching) == 1, "El evento no fue reclamado exactamente una vez")
    require(matching[0].attempts == 1, "El primer intento no fue contabilizado")
    print("Inserción transaccional: OK")
    print("Reclamación SKIP LOCKED: OK")

    repository.mark_failed(event_id, "fallo sintético controlado")
    claimed_again = repository.claim_batch(limit=100)
    matching_again = tuple(
        record for record in claimed_again if record.event_id == event_id
    )
    require(
        len(matching_again) == 1,
        "El evento fallido no volvió a quedar disponible",
    )
    require(
        matching_again[0].attempts == 2,
        "El segundo intento no fue contabilizado",
    )
    print("Reintento después de fallo: OK")

    repository.mark_published(event_id, message_id)
    repository.mark_published(event_id, message_id)

    try:
        repository.mark_published(event_id, f"{message_id}-different")
    except ValueError:
        print("Conflicto de message_id: OK")
    else:
        raise AssertionError(
            "Se aceptó un message_id diferente para un evento publicado"
        )

    with factory() as session:
        row = session.scalar(
            select(EventoOutbox).where(
                EventoOutbox.event_id == event_id
            )
        )
        require(row is not None, "El evento publicado no existe")
        require(row.estado == "publicado", "Estado final incorrecto")
        require(row.intentos == 2, "Cantidad final de intentos incorrecta")
        require(
            row.pubsub_message_id == message_id,
            "message_id no persistido",
        )
        require(row.publicado_en is not None, "Fecha de publicación ausente")

    print("Confirmación idempotente de publicación: OK")
    print("S3-BE-03 OUTBOX POSTGRESQL: OK")
finally:
    outer_transaction.rollback()
    connection.close()

with engine.connect() as verification:
    residual = verification.scalar(
        select(func.count())
        .select_from(EventoOutbox)
        .where(EventoOutbox.event_id == event_id)
    )

require(residual == 0, "La validación dejó un evento residual")
print("ROLLBACK ejecutado")
print("Limpieza validada: sin registros residuales")
print("VALIDACIÓN OUTBOX S3-BE-03 COMPLETADA")
engine.dispose()
