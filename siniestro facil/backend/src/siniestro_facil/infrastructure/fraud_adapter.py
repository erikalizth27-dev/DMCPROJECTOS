from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from siniestro_facil.domain.fraud import (
    AlertRecommendation,
    AlertSeverity,
    RiskSignal,
    RiskSignalType,
    SignalOrigin,
)


@dataclass(frozen=True, slots=True)
class DeterministicRule:
    fact_key: str
    signal_type: RiskSignalType
    severity: AlertSeverity
    explanation: str


@dataclass(frozen=True, slots=True)
class FraudEvaluation:
    signals: tuple[RiskSignal, ...]
    alerts: tuple[AlertRecommendation, ...]


class DeterministicFraudAdapter:
    """Adaptador piloto reproducible; no confirma fraude ni decide rechazos."""

    def __init__(
        self,
        *,
        rule_set: str,
        version: str,
        policy_version: str,
        rules: tuple[DeterministicRule, ...],
    ) -> None:
        if not rule_set.strip() or not version.strip() or not policy_version.strip():
            raise ValueError("Regla, versión y política son obligatorias")
        self._rule_set = rule_set.strip()
        self._version = version.strip()
        self._policy_version = policy_version.strip()
        self._rules = rules

    @property
    def identifier(self) -> str:
        return f"{self._rule_set}:{self._version}"

    def evaluate(self, facts: Mapping[str, object]) -> FraudEvaluation:
        signals: list[RiskSignal] = []
        alerts: list[AlertRecommendation] = []
        for rule in self._rules:
            if facts.get(rule.fact_key) is not True:
                continue
            source = {
                "fact_key": rule.fact_key,
                "fact_value": True,
            }
            signals.append(
                RiskSignal(
                    signal_type=rule.signal_type,
                    origin=SignalOrigin.DETERMINISTICA,
                    source_data=source,
                )
            )
            alerts.append(
                AlertRecommendation(
                    alert_type=rule.signal_type.value,
                    severity=rule.severity,
                    explanation=rule.explanation,
                    source_data=source,
                    rule_or_model=self.identifier,
                    policy_version=self._policy_version,
                )
            )
        return FraudEvaluation(tuple(signals), tuple(alerts))
