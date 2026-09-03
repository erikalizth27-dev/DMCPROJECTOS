from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Protocol

from siniestro_facil.domain.inspection_budget import BudgetStatus
from siniestro_facil.domain.identity import AuthenticatedPrincipal


@dataclass(frozen=True, slots=True)
class ClaimInspectionContext:
    claim_id: int
    current_state: str
    version: int


@dataclass(frozen=True, slots=True)
class InspectionRecord:
    id: int
    claim_id: int
    scheduled_at: datetime


@dataclass(frozen=True, slots=True)
class BudgetRecord:
    id: int
    claim_id: int
    provider_id: int
    diagnosis: str | None
    valid_from: date
    valid_until: date
    status: BudgetStatus


class InspectionBudgetRepository(Protocol):
    def find_claim_context(
        self,
        claim_id: int,
        principal: AuthenticatedPrincipal,
    ) -> ClaimInspectionContext | None: ...

    def find_inspection(
        self,
        claim_id: int,
        inspection_id: int,
        principal: AuthenticatedPrincipal,
    ) -> InspectionRecord | None: ...

    def find_budget(
        self,
        claim_id: int,
        budget_id: int,
        principal: AuthenticatedPrincipal,
    ) -> BudgetRecord | None: ...
