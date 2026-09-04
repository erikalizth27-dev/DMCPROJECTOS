from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from siniestro_facil.domain.audit import (
    AuditDetailLevel,
    TimelineEvent,
    TimelineEventView,
    audit_detail_level,
    project_timeline_event,
)
from siniestro_facil.domain.authorization import (
    Action,
    AuthorizationDenied,
    authorize,
)
from siniestro_facil.domain.identity import AuthenticatedPrincipal


class ClaimTimelineError(RuntimeError):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


@dataclass(frozen=True, slots=True)
class TimelineSlice:
    events: tuple[TimelineEvent, ...]
    next_cursor: int | None


@dataclass(frozen=True, slots=True)
class ClaimTimelineResult:
    claim_id: int
    events: tuple[TimelineEventView, ...]
    next_cursor: int | None
    detail_level: AuditDetailLevel


class ClaimTimelineRepository(Protocol):
    def list_visible(
        self,
        claim_id: int,
        principal: AuthenticatedPrincipal,
        *,
        after_event_id: int,
        page_size: int | None,
    ) -> TimelineSlice | None: ...

    def record_sensitive_access(
        self,
        claim_id: int,
        principal: AuthenticatedPrincipal,
        *,
        event_ids: tuple[int, ...],
    ) -> None: ...


class GetClaimTimelineService:
    def __init__(self, repository: ClaimTimelineRepository) -> None:
        self._repository = repository

    def execute(
        self,
        claim_id: int,
        principal: AuthenticatedPrincipal,
        *,
        after_event_id: int = 0,
        page_size: int | None = None,
    ) -> ClaimTimelineResult:
        if claim_id <= 0 or after_event_id < 0:
            raise ClaimTimelineError(
                "CLAIM-TIMELINE-INVALID",
                "Siniestro o cursor inválido",
                422,
            )
        if page_size is not None and page_size <= 0:
            raise ClaimTimelineError(
                "CLAIM-TIMELINE-INVALID",
                "La cantidad solicitada debe ser mayor que cero",
                422,
            )
        try:
            authorize(
                principal.role,
                Action.CONSULTAR_AUDITORIA,
                resource_in_scope=True,
            )
        except AuthorizationDenied as exc:
            raise ClaimTimelineError(
                "CLAIM-TIMELINE-FORBIDDEN",
                "Acción no permitida para el rol",
                403,
            ) from exc

        raw = self._repository.list_visible(
            claim_id,
            principal,
            after_event_id=after_event_id,
            page_size=page_size,
        )
        if raw is None:
            raise ClaimTimelineError(
                "CLAIM-TIMELINE-NOT-FOUND",
                "Siniestro no encontrado",
                404,
            )

        events = tuple(
            project_timeline_event(event, principal.role)
            for event in raw.events
        )
        level = audit_detail_level(principal.role)
        if level in {
            AuditDetailLevel.INVESTIGACION,
            AuditDetailLevel.COMPLETO,
        }:
            sensitive_ids = tuple(
                event.event_id for event in raw.events if event.sensitive
            )
            if sensitive_ids:
                self._repository.record_sensitive_access(
                    claim_id,
                    principal,
                    event_ids=sensitive_ids,
                )

        return ClaimTimelineResult(
            claim_id=claim_id,
            events=events,
            next_cursor=raw.next_cursor,
            detail_level=level,
        )
