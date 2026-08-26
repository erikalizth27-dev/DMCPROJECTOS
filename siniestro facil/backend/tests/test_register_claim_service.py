from dataclasses import replace
from datetime import date, datetime, timezone
from decimal import Decimal
import unittest

from siniestro_facil.application.register_claim import (
    ClaimRegistrationError,
    InMemoryClaimRepository,
    RegisterClaimCommand,
    RegisterClaimService,
)
from siniestro_facil.infrastructure.policy_adapter import (
    InMemoryPolicyAdapter,
    PolicySnapshot,
)


class RegisterClaimServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.service = RegisterClaimService(
            InMemoryPolicyAdapter(
                [
                    PolicySnapshot(
                        numero_poliza="POL-SYN-001",
                        numero_documento="DOC-SYN-001",
                        placa="SYN0001",
                        vigente_desde=date(2026, 1, 1),
                        vigente_hasta=date(2026, 12, 31),
                        deducible=Decimal("500.00"),
                    )
                ]
            ),
            InMemoryClaimRepository(),
        )
        self.command = RegisterClaimCommand(
            numero_poliza="POL-SYN-001",
            numero_documento=None,
            placa="SYN0001",
            fecha_evento=datetime(2026, 8, 25, 14, 30, tzinfo=timezone.utc),
            ubicacion_evento="Ubicación sintética",
            tipo_evento="colision",
            medio_contacto="synthetic@example.invalid",
        )
        self.payload = {
            "numeroPoliza": "POL-SYN-001",
            "placa": "SYN0001",
            "fechaEvento": "2026-08-25T14:30:00Z",
        }

    def execute(self, payload=None):
        return self.service.execute(
            self.command,
            idempotency_key="idem-synthetic-0001",
            request_payload=self.payload if payload is None else payload,
        )

    def test_registers_claim_in_reported_state(self) -> None:
        result = self.execute()
        self.assertEqual("reportado", result.estado_actual)
        self.assertEqual("validar_cobertura", result.siguiente_paso)

    def test_replays_same_result_for_same_key_and_payload(self) -> None:
        first = self.execute()
        second = self.execute()
        self.assertEqual(first, second)

    def test_rejects_same_key_with_different_payload(self) -> None:
        self.execute()
        with self.assertRaisesRegex(ClaimRegistrationError, "otro contenido") as caught:
            self.execute({"numeroPoliza": "POL-SYN-OTHER"})
        self.assertEqual(409, caught.exception.status_code)

    def test_rejects_unknown_policy(self) -> None:
        command = replace(self.command, numero_poliza="POL-UNKNOWN")
        with self.assertRaisesRegex(ClaimRegistrationError, "póliza elegible"):
            self.service.execute(
                command,
                idempotency_key="idem-synthetic-0002",
                request_payload={"numeroPoliza": "POL-UNKNOWN"},
            )

    def test_rejects_plate_not_covered(self) -> None:
        command = RegisterClaimCommand(
            numero_poliza=self.command.numero_poliza,
            numero_documento=None,
            placa="OTHER01",
            fecha_evento=self.command.fecha_evento,
            ubicacion_evento=self.command.ubicacion_evento,
            tipo_evento=self.command.tipo_evento,
            medio_contacto=self.command.medio_contacto,
        )
        with self.assertRaisesRegex(ClaimRegistrationError, "placa"):
            self.service.execute(
                command,
                idempotency_key="idem-synthetic-0003",
                request_payload={"placa": "OTHER01"},
            )

    def test_rejects_event_outside_policy_validity(self) -> None:
        command = RegisterClaimCommand(
            numero_poliza=self.command.numero_poliza,
            numero_documento=None,
            placa=self.command.placa,
            fecha_evento=datetime(2027, 1, 1, tzinfo=timezone.utc),
            ubicacion_evento=self.command.ubicacion_evento,
            tipo_evento=self.command.tipo_evento,
            medio_contacto=self.command.medio_contacto,
        )
        with self.assertRaisesRegex(ClaimRegistrationError, "vigente"):
            self.service.execute(
                command,
                idempotency_key="idem-synthetic-0004",
                request_payload={"fechaEvento": "2027-01-01T00:00:00Z"},
            )

    def test_rejects_invalid_idempotency_key(self) -> None:
        with self.assertRaisesRegex(ClaimRegistrationError, "entre 16 y 128"):
            self.service.execute(
                self.command,
                idempotency_key="short",
                request_payload=self.payload,
            )


if __name__ == "__main__":
    unittest.main()
