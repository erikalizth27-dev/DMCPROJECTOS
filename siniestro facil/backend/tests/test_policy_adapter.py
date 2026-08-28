from datetime import date
from decimal import Decimal
import unittest

from siniestro_facil.infrastructure.policy_adapter import (
    InMemoryPolicyAdapter,
    PolicySnapshot,
)


def policy() -> PolicySnapshot:
    return PolicySnapshot(
        numero_poliza="POL-SYN-001",
        numero_documento="DOC-SYN-001",
        placa="SYN001",
        vigente_desde=date(2026, 1, 1),
        vigente_hasta=date(2026, 12, 31),
        deducible=Decimal("500.00"),
    )


class InMemoryPolicyAdapterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = InMemoryPolicyAdapter([policy()])

    def test_finds_policy_by_normalized_number(self) -> None:
        self.assertEqual(policy(), self.adapter.find(numero_poliza=" pol-syn-001 "))

    def test_finds_policy_by_document(self) -> None:
        self.assertEqual(policy(), self.adapter.find(numero_documento="doc-syn-001"))

    def test_requires_both_identifiers_to_match_same_policy(self) -> None:
        self.assertIsNone(
            self.adapter.find(
                numero_poliza="POL-SYN-001",
                numero_documento="DOC-UNKNOWN",
            )
        )

    def test_requires_at_least_one_identifier(self) -> None:
        with self.assertRaisesRegex(ValueError, "Debe indicar"):
            self.adapter.find()

    def test_rejects_duplicate_synthetic_policy(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicada"):
            InMemoryPolicyAdapter([policy(), policy()])

    def test_checks_event_date_against_coverage(self) -> None:
        self.assertTrue(policy().is_active_on(date(2026, 8, 25)))
        self.assertFalse(policy().is_active_on(date(2027, 1, 1)))


if __name__ == "__main__":
    unittest.main()
