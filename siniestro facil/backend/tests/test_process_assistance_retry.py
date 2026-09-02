from datetime import datetime, timezone

import pytest

from siniestro_facil.application.assistance_contracts import AssistanceRecord
from siniestro_facil.application.process_assistance_retry import (
    PILOT_RETRY_POLICY,
    RetryAction,
    RetryDecisionError,
    decide_assistance_retry,
)
from siniestro_facil.domain.assistance import AssistanceStatus


def record(
    *,
    status: AssistanceStatus = AssistanceStatus.NO_RESPONSE,
    attempt: int = 1,
) -> AssistanceRecord:
    now = datetime.now(timezone.utc)
    return AssistanceRecord(
        id=10,
        claim_id=42,
        provider_id=7,
        assistance_type="grua",
        status=status,
        attempt=attempt,
        created_at=now,
        updated_at=now,
    )


def test_pilot_policy_matches_approved_decision() -> None:
    assert PILOT_RETRY_POLICY.delays_seconds == (30, 120, 300)
    assert PILOT_RETRY_POLICY.timeout_seconds == 10
    assert PILOT_RETRY_POLICY.max_attempts == 3


@pytest.mark.parametrize(
    ("attempt", "delay", "next_attempt"),
    [
        (1, 30, 2),
        (2, 120, 3),
    ],
)
def test_schedules_retry(
    attempt: int,
    delay: int,
    next_attempt: int,
) -> None:
    decision = decide_assistance_retry(record(attempt=attempt))
    assert decision.action is RetryAction.RETRY
    assert decision.delay_seconds == delay
    assert decision.next_attempt == next_attempt
    assert decision.timeout_seconds == 10


def test_escalates_after_third_failure() -> None:
    decision = decide_assistance_retry(record(attempt=3))
    assert decision.action is RetryAction.ESCALATE
    assert decision.delay_seconds == 300
    assert decision.next_attempt is None


def test_allows_rejected_provider_result() -> None:
    decision = decide_assistance_retry(
        record(status=AssistanceStatus.REJECTED)
    )
    assert decision.action is RetryAction.RETRY


@pytest.mark.parametrize(
    "status",
    [
        AssistanceStatus.PENDING,
        AssistanceStatus.SENT,
        AssistanceStatus.ACCEPTED,
        AssistanceStatus.ESCALATED,
    ],
)
def test_rejects_non_retryable_status(
    status: AssistanceStatus,
) -> None:
    with pytest.raises(RetryDecisionError):
        decide_assistance_retry(record(status=status))
