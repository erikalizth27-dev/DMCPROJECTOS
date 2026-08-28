from datetime import datetime, timezone

from siniestro_facil.persistence.claim_repository import PostgreSQLClaimRepository
from siniestro_facil.persistence.models import SolicitudIdempotente


def test_rebuilds_registered_claim_from_persisted_response() -> None:
    row = SolicitudIdempotente(
        clave="idem-synthetic-0001",
        huella="a" * 64,
        id_siniestro=42,
        respuesta={
            "id": 42,
            "estado_actual": "reportado",
            "fecha_evento": "2026-08-25T14:30:00+00:00",
            "tipo_evento": "colision",
            "siguiente_paso": "validar_cobertura",
        },
        creado_en=datetime.now(timezone.utc),
    )

    result = PostgreSQLClaimRepository._result_from_row(row)

    assert result.id == 42
    assert result.estado_actual == "reportado"
    assert result.fecha_evento == datetime(2026, 8, 25, 14, 30, tzinfo=timezone.utc)
    assert result.siguiente_paso == "validar_cobertura"
