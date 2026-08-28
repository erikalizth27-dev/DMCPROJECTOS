from datetime import date
from decimal import Decimal
import unittest

from fastapi.testclient import TestClient

from siniestro_facil.api.routes.claims import get_register_claim_service
from siniestro_facil.application.register_claim import (
    InMemoryClaimRepository,
    RegisterClaimService,
)
from siniestro_facil.infrastructure.policy_adapter import (
    InMemoryPolicyAdapter,
    PolicySnapshot,
)
from siniestro_facil.main import create_app


class ClaimsApiTest(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app()
        service = RegisterClaimService(
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
        self.app.dependency_overrides[get_register_claim_service] = lambda: service
        self.client = TestClient(self.app)
        self.payload = {
            "numeroPoliza": "POL-SYN-001",
            "placa": "SYN0001",
            "fechaEvento": "2026-08-25T14:30:00Z",
            "ubicacionEvento": "Ubicación sintética",
            "tipoEvento": "colision",
            "medioContacto": "synthetic@example.invalid",
        }
        self.headers = {
            "Idempotency-Key": "idem-synthetic-0001",
            "X-Correlation-ID": "corr-synthetic-0001",
        }

    def test_creates_claim_with_http_201(self) -> None:
        response = self.client.post(
            "/api/v1/siniestros", json=self.payload, headers=self.headers
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual("reportado", response.json()["estadoActual"])
        self.assertEqual("corr-synthetic-0001", response.headers["X-Correlation-ID"])

    def test_replays_same_claim_for_same_request(self) -> None:
        first = self.client.post(
            "/api/v1/siniestros", json=self.payload, headers=self.headers
        )
        second = self.client.post(
            "/api/v1/siniestros", json=self.payload, headers=self.headers
        )
        self.assertEqual(first.json(), second.json())

    def test_returns_contract_error_for_idempotency_conflict(self) -> None:
        self.client.post("/api/v1/siniestros", json=self.payload, headers=self.headers)
        changed = {**self.payload, "tipoEvento": "robo"}
        response = self.client.post(
            "/api/v1/siniestros", json=changed, headers=self.headers
        )
        self.assertEqual(409, response.status_code)
        self.assertEqual("IDEMPOTENCY-CONFLICT", response.json()["codigo"])
        self.assertEqual([], response.json()["detalles"])

    def test_requires_idempotency_header(self) -> None:
        response = self.client.post("/api/v1/siniestros", json=self.payload)
        self.assertEqual(422, response.status_code)

    def test_rejects_vehicle_outside_validated_policy(self) -> None:
        response = self.client.post(
            "/api/v1/siniestros",
            json={**self.payload, "placa": "OTHER01"},
            headers={**self.headers, "Idempotency-Key": "idem-synthetic-0002"},
        )
        self.assertEqual(422, response.status_code)
        self.assertEqual("VEHICLE-NOT-COVERED", response.json()["codigo"])

    def test_returns_private_conflict_for_possible_duplicate(self) -> None:
        first = self.client.post(
            "/api/v1/siniestros", json=self.payload, headers=self.headers
        )
        response = self.client.post(
            "/api/v1/siniestros",
            json={**self.payload, "ubicacionEvento": "Otra ubicación"},
            headers={**self.headers, "Idempotency-Key": "idem-duplicate-0002"},
        )

        self.assertEqual(201, first.status_code)
        self.assertEqual(409, response.status_code)
        body = response.json()
        self.assertEqual("POSSIBLE-DUPLICATE", body["codigo"])
        self.assertEqual([], body["detalles"])
        self.assertNotIn("id", body)
        self.assertNotIn("idSiniestro", body)


if __name__ == "__main__":
    unittest.main()
