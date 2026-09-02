from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from siniestro_facil.domain.assistance import AssistanceStatus, ProviderResult


@dataclass(frozen=True, slots=True)
class AssistanceRequest:
    claim_id: int
    provider_id: int
    assistance_type: str
    requested_at: datetime
    reason: str


@dataclass(frozen=True, slots=True)
class AssistanceRecord:
    id: int
    claim_id: int
    provider_id: int
    assistance_type: str
    status: AssistanceStatus
    attempt: int
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class ProviderReply:
    assistance_id: int
    result: ProviderResult
    received_at: datetime
    external_reference: str | None = None


class AssistanceRepository(Protocol):
    def create(
        self,
        request: AssistanceRequest,
        *,
        idempotency_key: str,
        fingerprint: str,
    ) -> AssistanceRecord: ...

    def get(self, assistance_id: int) -> AssistanceRecord | None: ...

    def register_reply(
        self,
        reply: ProviderReply,
        *,
        expected_attempt: int,
    ) -> AssistanceRecord: ...


class AssistanceEventPublisher(Protocol):
    def publish_pending(self, *, limit: int) -> int: ...
