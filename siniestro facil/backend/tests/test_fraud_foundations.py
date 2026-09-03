import unittest

from siniestro_facil.domain.fraud import (
    AlertEffect,
    AlertSeverity,
    RelationCriterion,
    RiskSignalType,
    canonical_claim_pair,
    effect_for_severity,
    normalize_exact_value,
)
from siniestro_facil.infrastructure.fraud_adapter import (
    DeterministicFraudAdapter,
    DeterministicRule,
)


class FraudDomainTest(unittest.TestCase):
    def test_critical_alert_blocks_payment_until_review(self) -> None:
        self.assertEqual(
            AlertEffect.BLOQUEAR_PAGO_HASTA_REVISION,
            effect_for_severity(AlertSeverity.CRITICA),
        )

    def test_high_alert_routes_to_investigation(self) -> None:
        self.assertEqual(
            AlertEffect.DERIVAR_INVESTIGACION,
            effect_for_severity(AlertSeverity.ALTA),
        )

    def test_medium_and_low_alerts_only_raise_priority(self) -> None:
        for severity in (AlertSeverity.MEDIA, AlertSeverity.BAJA):
            self.assertEqual(
                AlertEffect.PRIORIZAR,
                effect_for_severity(severity),
            )

    def test_exact_value_normalization_is_stable(self) -> None:
        self.assertEqual(
            "TALLER CENTRAL",
            normalize_exact_value("  Taller   Central  "),
        )

    def test_claim_pair_is_canonical(self) -> None:
        self.assertEqual((4, 9), canonical_claim_pair(9, 4))

    def test_claim_cannot_be_related_to_itself(self) -> None:
        with self.assertRaisesRegex(ValueError, "consigo mismo"):
            canonical_claim_pair(4, 4)

    def test_relation_catalog_matches_physical_model(self) -> None:
        self.assertEqual(
            {"accidente", "telefono", "cuenta_bancaria", "taller", "persona"},
            {item.value for item in RelationCriterion},
        )


class DeterministicFraudAdapterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = DeterministicFraudAdapter(
            rule_set="pilot-fraud",
            version="1",
            policy_version="pilot-1",
            rules=(
                DeterministicRule(
                    fact_key="foto_reutilizada",
                    signal_type=RiskSignalType.FOTO_REUTILIZADA,
                    severity=AlertSeverity.ALTA,
                    explanation="Coincidencia exacta de hash disponible",
                ),
            ),
        )

    def test_evaluation_is_reproducible(self) -> None:
        first = self.adapter.evaluate({"foto_reutilizada": True})
        second = self.adapter.evaluate({"foto_reutilizada": True})
        self.assertEqual(first, second)
        self.assertEqual("pilot-fraud:1", first.alerts[0].rule_or_model)
        self.assertEqual("pilot-1", first.alerts[0].policy_version)

    def test_only_explicit_true_fact_generates_candidate(self) -> None:
        for value in (False, None, "true", 1):
            result = self.adapter.evaluate({"foto_reutilizada": value})
            self.assertEqual((), result.signals)
            self.assertEqual((), result.alerts)

    def test_alert_is_recommendation_not_fraud_confirmation(self) -> None:
        result = self.adapter.evaluate({"foto_reutilizada": True})
        self.assertEqual(AlertSeverity.ALTA, result.alerts[0].severity)
        self.assertEqual(
            AlertEffect.DERIVAR_INVESTIGACION,
            result.alerts[0].effect,
        )

    def test_requires_versioned_configuration(self) -> None:
        with self.assertRaisesRegex(ValueError, "obligatorias"):
            DeterministicFraudAdapter(
                rule_set="pilot-fraud",
                version="",
                policy_version="pilot-1",
                rules=(),
            )


if __name__ == "__main__":
    unittest.main()
