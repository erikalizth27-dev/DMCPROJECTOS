from datetime import datetime, timedelta, timezone

import pytest

from siniestro_facil.application.evaluate_fraud import (
    EvaluateFraudCommand,
    EvaluateFraudService,
    FraudEvaluationError,
    InMemoryFraudAlertRepository,
    ReviewAlertCommand,
    ReviewFraudAlertService,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.fraud import (
    AlertReviewStatus,
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
        subject=f"{role.value}-review-service",
        role=role,
        actor_type=ActorType.INTERNO,
        tenant_id="tenant-synthetic",
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


def configured():
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
    investigator = principal(PrincipalRole.INVESTIGADOR_FRAUDE)
    created = EvaluateFraudService(adapter, repository).execute(
        EvaluateFraudCommand(42, {"foto_reutilizada": True}),
        investigator,
        idempotency_key="fraud-review-setup-0001",
        request_payload={"hechos": {"foto_reutilizada": True}},
    )
    return (
        ReviewFraudAlertService(repository),
        created.alerts[0].id,
        investigator,
    )


def execute(
    service,
    alert_id,
    reviewer,
    *,
    target=AlertReviewStatus.CONFIRMADA,
    justification="Revisión humana documentada",
    version=0,
    key="fraud-alert-review-0001",
):
    payload = {
        "estado": target.value,
        "justificacion": justification,
        "version": version,
    }
    return service.execute(
        ReviewAlertCommand(42, alert_id, target, justification, version),
        reviewer,
        idempotency_key=key,
        request_payload=payload,
    )


@pytest.mark.parametrize(
    "target",
    [
        AlertReviewStatus.CONFIRMADA,
        AlertReviewStatus.DESCARTADA,
        AlertReviewStatus.EN_SOLICITUD_INFO,
    ],
)
def test_investigator_records_each_human_decision(target) -> None:
    service, alert_id, investigator = configured()
    result = execute(service, alert_id, investigator, target=target)
    assert result.review_status is target
    assert result.version == 1
    assert result.reviewer_subject == investigator.subject


def test_supervisor_can_review() -> None:
    service, alert_id, _ = configured()
    result = execute(
        service,
        alert_id,
        principal(PrincipalRole.SUPERVISOR),
    )
    assert result.review_status is AlertReviewStatus.CONFIRMADA


def test_operator_cannot_review() -> None:
    service, alert_id, _ = configured()
    with pytest.raises(FraudEvaluationError) as error:
        execute(service, alert_id, principal(PrincipalRole.OPERADOR))
    assert error.value.code == "ALERT-REVIEW-FORBIDDEN"


def test_justification_is_required() -> None:
    service, alert_id, investigator = configured()
    with pytest.raises(FraudEvaluationError) as error:
        execute(service, alert_id, investigator, justification="   ")
    assert error.value.code == "ALERT-REVIEW-JUSTIFICATION-REQUIRED"


def test_pending_is_not_a_human_decision() -> None:
    service, alert_id, investigator = configured()
    with pytest.raises(FraudEvaluationError) as error:
        execute(
            service,
            alert_id,
            investigator,
            target=AlertReviewStatus.PENDIENTE,
        )
    assert error.value.code == "ALERT-REVIEW-INVALID"


def test_repetition_is_idempotent() -> None:
    service, alert_id, investigator = configured()
    first = execute(service, alert_id, investigator)
    repeated = execute(service, alert_id, investigator)
    assert repeated == first


def test_different_content_conflicts() -> None:
    service, alert_id, investigator = configured()
    execute(service, alert_id, investigator)
    with pytest.raises(FraudEvaluationError) as error:
        execute(
            service,
            alert_id,
            investigator,
            target=AlertReviewStatus.DESCARTADA,
        )
    assert error.value.code == "IDEMPOTENCY-CONFLICT"


def test_stale_version_conflicts() -> None:
    service, alert_id, investigator = configured()
    execute(service, alert_id, investigator)
    with pytest.raises(FraudEvaluationError) as error:
        execute(
            service,
            alert_id,
            investigator,
            target=AlertReviewStatus.DESCARTADA,
            key="fraud-alert-review-0002",
        )
    assert error.value.code == "ALERT-VERSION-CONFLICT"
