from datetime import datetime, timedelta, timezone

import pytest

from siniestro_facil.application.get_claim_timeline import (
    ClaimTimelineError,
    GetClaimTimelineService,
    TimelineSlice,
)
from siniestro_facil.domain.audit import TimelineEvent
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal


class TimelineRepository:
    def __init__(self, *, visible: bool = True) -> None:
        self.visible = visible
        self.sensitive_accesses: list[tuple[int, tuple[int, ...]]] = []

    def list_visible(
        self, claim_id, principal, *, after_event_id, page_size
    ):
        if not self.visible:
            return None
        events = (
            TimelineEvent(
                event_id=11,
                claim_id=claim_id,
                event_type="evidencia_registrada",
                actor_id=2,
                detail={"tipo": "foto"},
                occurred_at=datetime(2026, 9, 3, tzinfo=timezone.utc),
            ),
            TimelineEvent(
                event_id=12,
                claim_id=claim_id,
                event_type="alerta_fraude_revisada",
                actor_id=3,
                detail={"explicacion": "reservada"},
                sensitive=True,
                occurred_at=datetime(2026, 9, 3, 1, tzinfo=timezone.utc),
            ),
        )
        selected = tuple(e for e in events if e.event_id > after_event_id)
        if page_size is not None:
            selected = selected[:page_size]
        return TimelineSlice(selected, selected[-1].event_id if selected else None)

    def record_sensitive_access(
        self, claim_id, principal, *, event_ids
    ) -> None:
        self.sensitive_accesses.append((claim_id, event_ids))


def make_principal(role: PrincipalRole) -> AuthenticatedPrincipal:
    now = datetime.now(timezone.utc)
    return AuthenticatedPrincipal(
        subject=f"subject-{role.value}",
        role=role,
        actor_type=ActorType.INTERNO,
        tenant_id="tenant-s6",
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


def test_operator_receives_redacted_sensitive_detail() -> None:
    repository = TimelineRepository()
    result = GetClaimTimelineService(repository).execute(
        4, make_principal(PrincipalRole.OPERADOR)
    )
    assert result.events[1].detail == {
        "resumen": "Información sensible restringida"
    }
    assert repository.sensitive_accesses == []


def test_supervisor_receives_complete_detail_and_access_is_audited() -> None:
    repository = TimelineRepository()
    result = GetClaimTimelineService(repository).execute(
        4, make_principal(PrincipalRole.SUPERVISOR)
    )
    assert result.events[1].detail["explicacion"] == "reservada"
    assert repository.sensitive_accesses == [(4, (12,))]


def test_investigator_receives_investigation_detail_and_is_audited() -> None:
    repository = TimelineRepository()
    result = GetClaimTimelineService(repository).execute(
        4, make_principal(PrincipalRole.INVESTIGADOR_FRAUDE)
    )
    assert result.events[1].detail["explicacion"] == "reservada"
    assert repository.sensitive_accesses == [(4, (12,))]


def test_cursor_and_requested_page_size_are_forwarded() -> None:
    result = GetClaimTimelineService(TimelineRepository()).execute(
        4,
        make_principal(PrincipalRole.OPERADOR),
        after_event_id=11,
        page_size=1,
    )
    assert [event.event_id for event in result.events] == [12]
    assert result.next_cursor == 12


def test_out_of_scope_is_private_not_found() -> None:
    with pytest.raises(ClaimTimelineError) as caught:
        GetClaimTimelineService(
            TimelineRepository(visible=False)
        ).execute(4, make_principal(PrincipalRole.OPERADOR))
    assert caught.value.code == "CLAIM-TIMELINE-NOT-FOUND"
    assert caught.value.status_code == 404


@pytest.mark.parametrize(
    ("claim_id", "cursor", "page_size"),
    [(0, 0, None), (4, -1, None), (4, 0, 0)],
)
def test_invalid_pagination_is_rejected(
    claim_id: int, cursor: int, page_size: int | None
) -> None:
    with pytest.raises(ClaimTimelineError) as caught:
        GetClaimTimelineService(TimelineRepository()).execute(
            claim_id,
            make_principal(PrincipalRole.SUPERVISOR),
            after_event_id=cursor,
            page_size=page_size,
        )
    assert caught.value.status_code == 422
