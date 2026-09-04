from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Mapping

from siniestro_facil.domain.authorization import PrincipalRole


class AuditDetailLevel(StrEnum):
    LIMITADO = "limitado"
    OPERATIVO = "operativo"
    INVESTIGACION = "investigacion"
    COMPLETO = "completo"


@dataclass(frozen=True, slots=True)
class TimelineEvent:
    event_id: int
    claim_id: int
    event_type: str
    actor_id: int | None
    detail: Mapping[str, object]
    sensitive: bool = False
    occurred_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class TimelineEventView:
    event_id: int
    claim_id: int
    event_type: str
    actor_id: int | None
    detail: Mapping[str, object]
    detail_level: AuditDetailLevel
    occurred_at: datetime | None


def audit_detail_level(role: PrincipalRole) -> AuditDetailLevel:
    if role is PrincipalRole.SUPERVISOR:
        return AuditDetailLevel.COMPLETO
    if role is PrincipalRole.INVESTIGADOR_FRAUDE:
        return AuditDetailLevel.INVESTIGACION
    if role in {PrincipalRole.OPERADOR, PrincipalRole.AJUSTADOR}:
        return AuditDetailLevel.OPERATIVO
    return AuditDetailLevel.LIMITADO


def project_timeline_event(
    event: TimelineEvent,
    role: PrincipalRole,
) -> TimelineEventView:
    level = audit_detail_level(role)
    can_view_sensitive = level in {
        AuditDetailLevel.INVESTIGACION,
        AuditDetailLevel.COMPLETO,
    }
    detail: Mapping[str, object]
    if event.sensitive and not can_view_sensitive:
        detail = {"resumen": "Información sensible restringida"}
    else:
        detail = dict(event.detail)
    return TimelineEventView(
        event_id=event.event_id,
        claim_id=event.claim_id,
        event_type=event.event_type,
        actor_id=event.actor_id,
        detail=detail,
        detail_level=level,
        occurred_at=event.occurred_at,
    )
