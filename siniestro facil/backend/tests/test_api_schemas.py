from datetime import date, datetime, timezone
from decimal import Decimal
import unittest

from pydantic import ValidationError

from siniestro_facil.api.schemas import (
    CrearSiniestroRequest,
    RegistrarPagoRequest,
    RegistrarPresupuestoRequest,
)


class ApiSchemasTest(unittest.TestCase):
    def test_claim_requires_policy_or_document(self) -> None:
        with self.assertRaisesRegex(ValidationError, "numeroPoliza o numeroDocumento"):
            CrearSiniestroRequest.model_validate(
                {
                    "placa": "SYN0001",
                    "fechaEvento": datetime.now(timezone.utc).isoformat(),
                    "ubicacionEvento": "Ubicacion sintetica",
                    "tipoEvento": "colision",
                    "medioContacto": "synthetic@example.invalid",
                }
            )

    def test_claim_accepts_minimum_contract(self) -> None:
        request = CrearSiniestroRequest.model_validate(
            {
                "numeroPoliza": "POL-001",
                "placa": "SYN0001",
                "fechaEvento": datetime.now(timezone.utc).isoformat(),
                "ubicacionEvento": "Ubicacion sintetica",
                "tipoEvento": "colision",
                "medioContacto": "synthetic@example.invalid",
            }
        )
        self.assertEqual("POL-001", request.numero_poliza)

    def test_budget_rejects_invalid_validity(self) -> None:
        with self.assertRaisesRegex(ValidationError, "vigenciaHasta"):
            RegistrarPresupuestoRequest.model_validate(
                {
                    "proveedorId": 1,
                    "vigenciaDesde": date(2026, 9, 1),
                    "vigenciaHasta": date(2026, 8, 1),
                }
            )

    def test_payment_requires_positive_amount(self) -> None:
        with self.assertRaises(ValidationError):
            RegistrarPagoRequest.model_validate(
                {"autorizacionId": 1, "monto": Decimal("0.00")}
            )

    def test_unknown_fields_are_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            RegistrarPagoRequest.model_validate(
                {"autorizacionId": 1, "monto": "10.00", "password": "never"}
            )


if __name__ == "__main__":
    unittest.main()
