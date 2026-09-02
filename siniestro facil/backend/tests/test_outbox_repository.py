from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from siniestro_facil.persistence.models import EventoOutbox
from siniestro_facil.persistence.outbox_repository import (
    PostgreSQLOutboxRepository,
)


def test_enqueue_uses_caller_transaction() -> None:
    session = Mock()
    occurred_at = datetime.now(timezone.utc)

    row = PostgreSQLOutboxRepository.enqueue(
        session,
        event_id="00000000-0000-4000-8000-000000000001",
        aggregate_type="asistencia",
        aggregate_id=41,
        event_type="asistencia.reintento_solicitado",
        payload={"id_asistencia": 41, "numero_intento": 2},
        occurred_at=occurred_at,
    )

    session.add.assert_called_once_with(row)
    assert isinstance(row, EventoOutbox)
    assert row.estado == "pendiente"
    assert row.intentos == 0
    assert row.disponible_en == occurred_at


@pytest.mark.parametrize("limit", [0, 501])
def test_claim_batch_rejects_invalid_limit(limit: int) -> None:
    repository = PostgreSQLOutboxRepository(Mock())

    with pytest.raises(ValueError, match="limit"):
        repository.claim_batch(limit=limit)


def test_outbox_model_has_unique_event_id_and_delivery_state() -> None:
    table = EventoOutbox.__table__

    assert table.schema == "siniestro_facil"
    assert table.columns.event_id.unique
    assert not table.columns.payload.nullable
    assert not table.columns.estado.nullable
    assert not table.columns.intentos.nullable
