from datetime import datetime, timedelta, timezone

import pytest

from siniestro_facil.application.evaluate_fraud import (
    EvaluateFraudCommand,
    EvaluateFraudService,
    FraudEvaluationError,
    GetFraudAlertService,
    InMemoryFraudAlertRepository,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.fraud import (
    AlertEffect,
    AlertSeverity,
    RiskSignalType,
)
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal
from siniestro_facil.infrastructure.fraud_adapter import (
    DeterministicFraudAdapter,
    DeterministicRule,
)


def principal(role: PrincipalRole) -> AuthenticatedPrincipal:
    now = datetime.now(timezone.utc)
    return AuthenticatedPrincipal(
        subject=f"{role.value}-fraud-service",
        role=role,
        actor_type=ActorType.INTERNO,
        tenant_id="tenant-synthetic",
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


def configured() -> tuple[
    EvaluateFraudService,
    GetFraudAlertService,
    InMemoryFraudAlertRepository,
]:
    repository = InMemoryFraudAlertRepository()
    adapter = DeterministicFraudAdapter(
        rule_set="pilot",
        version="1",
        policy_version="policy-1",
        rules=(
            DeterministicRule(
                "foto_reutilizada",
                RiskSignalType.FOTO_REUTILIZADA,
                AlertSeverity.CRITICA,
                "Hash exacto repetido",
            ),
        ),
    )
    return (
        EvaluateFraudService(adapter, repository),
        GetFraudAlertService(repository),
        repository,
    )


def execute(
    service: EvaluateFraudService,
    role: PrincipalRole = PrincipalRole.INVESTIGADOR_FRAUDE,
    facts: dict[str, object] | None = None,
    key: str = "fraud-evaluation-0001",
):
    payload = {"hechos": facts or {"foto_reutilizada": True}}
    return service.execute(
        EvaluateFraudCommand(42, payload["hechos"]),
        principal(role),
        idempotency_key=key,
        request_payload=payload,
    )


def test_critical_signal_creates_reproducible_alert() -> None:
    service, _, _ = configured()
    result = execute(service)
    alert = result.alerts[0]
    assert alert.severity is AlertSeverity.CRITICA
    assert alert.effect is AlertEffect.BLOQUEAR_PAGO_HASTA_REVISION
    assert alert.rule_or_model == "pilot:1"
    assert alert.policy_version == "policy-1"


def test_no_explicit_signal_creates_no_alert() -> None:
    service, _, _ = configured()
    result = execute(service, facts={"foto_reutilizada": False})
    assert result.alerts == ()


def test_operator_cannot_trigger_evaluation() -> None:
    service, _, _ = configured()
    with pytest.raises(FraudEvaluationError) as error:
        execute(service, PrincipalRole.OPERADOR)
    assert error.value.status_code == 403


def test_repetition_is_idempotent() -> None:
    service, _, _ = configured()
    first = execute(service)
    repeated = execute(service)
    assert repeated == first


def test_different_payload_conflicts() -> None:
    service, _, _ = configured()
    execute(service)
    with pytest.raises(FraudEvaluationError) as error:
        execute(service, facts={"foto_reutilizada": False})
    assert error.value.code == "IDEMPOTENCY-CONFLICT"


def test_operator_only_receives_alert_summary() -> None:
    evaluator, getter, _ = configured()
    alert_id = execute(evaluator).alerts[0].id
    view = getter.execute(42, alert_id, principal(PrincipalRole.OPERADOR))
    assert view.detail_level.value == "resumen"
    assert view.explanation is None
    assert view.source_data is None
    assert view.rule_or_model is None


def test_investigator_receives_reproducible_detail() -> None:
    evaluator, getter, _ = configured()
    alert_id = execute(evaluator).alerts[0].id
    view = getter.execute(
        42,
        alert_id,
        principal(PrincipalRole.INVESTIGADOR_FRAUDE),
    )
    assert view.detail_level.value == "detalle"
    assert view.explanation == "Hash exacto repetido"
    assert view.source_data == {
        "fact_key": "foto_reutilizada",
        "fact_value": True,
    }
