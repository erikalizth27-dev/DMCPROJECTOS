from datetime import datetime, timedelta, timezone

import pytest

from siniestro_facil.application.get_operational_metrics import (
    GetOperationalMetricsService,
    OperationalMetricFacts,
    OperationalMetricsError,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal
from siniestro_facil.domain.operational_metrics import (
    IndicatorAvailability,
    IndicatorName,
)


class FactsRepository:
    def __init__(self, facts: OperationalMetricFacts) -> None:
        self.facts = facts
        self.period = None

    def load_facts(self, *, period_start, period_end, principal):
        self.period = (period_start, period_end)
        return self.facts


def principal(role: PrincipalRole) -> AuthenticatedPrincipal:
    now = datetime.now(timezone.utc)
    return AuthenticatedPrincipal(
        subject=f"metrics-{role.value}",
        role=role,
        actor_type=ActorType.INTERNO,
        tenant_id="tenant-s6",
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


def period():
    start = datetime(2026, 9, 1, tzinfo=timezone.utc)
    return start, start + timedelta(days=1)


def test_calculates_only_metrics_with_required_events() -> None:
    start, end = period()
    repository = FactsRepository(
        OperationalMetricFacts(
            claim_created_at=start + timedelta(hours=1),
            first_assistance_at=start + timedelta(hours=1, minutes=5),
            first_decision_at=start + timedelta(hours=2),
        )
    )
    result = GetOperationalMetricsService(repository).execute(
        period_start=start,
        period_end=end,
        principal=principal(PrincipalRole.SUPERVISOR),
    )
    by_name = {item.name: item for item in result.indicators}
    assert by_name[
        IndicatorName.TIEMPO_PRIMERA_ASISTENCIA
    ].value_seconds == 300
    assert by_name[IndicatorName.TIEMPO_HASTA_DECISION].value_seconds == 3600
    assert repository.period == (start, end)


def test_missing_event_is_unavailable_not_zero() -> None:
    start, end = period()
    result = GetOperationalMetricsService(
        FactsRepository(OperationalMetricFacts(start, None, None))
    ).execute(
        period_start=start,
        period_end=end,
        principal=principal(PrincipalRole.SUPERVISOR),
    )
    assert result.indicators[0].availability is IndicatorAvailability.NO_DISPONIBLE
    assert result.indicators[0].value_seconds is None
    assert result.indicators[1].value_seconds is None


@pytest.mark.parametrize(
    "name",
    [
        IndicatorName.SATISFACCION_CLIENTE,
        IndicatorName.COSTO_OPERATIVO,
        IndicatorName.PERDIDAS_EVITADAS_FRAUDE,
    ],
)
def test_unapproved_sources_are_explicitly_unavailable(name) -> None:
    start, end = period()
    result = GetOperationalMetricsService(
        FactsRepository(OperationalMetricFacts(None, None, None))
    ).execute(
        period_start=start,
        period_end=end,
        principal=principal(PrincipalRole.SUPERVISOR),
    )
    indicator = next(item for item in result.indicators if item.name is name)
    assert indicator.availability is IndicatorAvailability.NO_DISPONIBLE
    assert indicator.value_seconds is None
    assert indicator.sources == ()
    assert indicator.reason == "Fuente de datos no definida"


def test_non_supervisor_is_forbidden() -> None:
    start, end = period()
    with pytest.raises(OperationalMetricsError) as caught:
        GetOperationalMetricsService(
            FactsRepository(OperationalMetricFacts(None, None, None))
        ).execute(
            period_start=start,
            period_end=end,
            principal=principal(PrincipalRole.OPERADOR),
        )
    assert caught.value.status_code == 403


def test_invalid_period_is_rejected() -> None:
    start, end = period()
    with pytest.raises(OperationalMetricsError) as caught:
        GetOperationalMetricsService(
            FactsRepository(OperationalMetricFacts(None, None, None))
        ).execute(
            period_start=end,
            period_end=start,
            principal=principal(PrincipalRole.SUPERVISOR),
        )
    assert caught.value.status_code == 422
