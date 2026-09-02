from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.enums import EstadoSiniestro
from siniestro_facil.domain.identity import AuthenticatedPrincipal
from siniestro_facil.domain.inspection_budget import (
    BudgetDecision,
    BudgetDecisionDenied,
    BudgetStatus,
    validate_budget_decision,
)


class BudgetDecisionError(ValueError):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


@dataclass(frozen=True, slots=True)
class DecideBudgetCommand:
    claim_id: int
    budget_id: int
    target: BudgetStatus
    reason: str
    expected_version: int


@dataclass(frozen=True, slots=True)
class DecidedBudget:
    decision_id: int
    budget_id: int
    claim_id: int
    target: BudgetStatus
    reason: str
    decided_at: datetime
    current_state: EstadoSiniestro
    version: int


class BudgetDecisionRepository(Protocol):
    def decide(
        self,
        command: DecideBudgetCommand,
        principal: AuthenticatedPrincipal,
    ) -> DecidedBudget: ...


class InMemoryBudgetDecisionRepository:
    def __init__(self) -> None:
        self._next_id = 1
        self._results: dict[int, DecidedBudget] = {}

    def decide(
        self,
        command: DecideBudgetCommand,
        principal: AuthenticatedPrincipal,
    ) -> DecidedBudget:
        state = {
            BudgetStatus.OBSERVED: EstadoSiniestro.OBSERVADO,
            BudgetStatus.AUTHORIZED: EstadoSiniestro.AUTORIZADO,
            BudgetStatus.REJECTED: EstadoSiniestro.RECHAZADO,
        }[command.target]
        result = DecidedBudget(
            decision_id=self._next_id,
            budget_id=command.budget_id,
            claim_id=command.claim_id,
            target=command.target,
            reason=command.reason.strip(),
            decided_at=datetime.now(timezone.utc),
            current_state=state,
            version=command.expected_version + 1,
        )
        self._results[result.decision_id] = result
        self._next_id += 1
        return result


class DecideBudgetService:
    def __init__(self, repository: BudgetDecisionRepository) -> None:
        self._repository = repository

    def execute(
        self,
        command: DecideBudgetCommand,
        principal: AuthenticatedPrincipal,
    ) -> DecidedBudget:
        if (
            command.claim_id <= 0
            or command.budget_id <= 0
            or command.expected_version < 0
        ):
            raise BudgetDecisionError(
                "BUDGET-DECISION-INVALID",
                "Siniestro, presupuesto o versión inválidos",
                422,
            )
        if not command.reason.strip():
            raise BudgetDecisionError(
                "BUDGET-DECISION-REASON-REQUIRED",
                "La justificación es obligatoria",
                422,
            )
        try:
            validate_budget_decision(
                BudgetDecision(
                    role=principal.role,
                    target=command.target,
                    actor_assigned=True,
                )
            )
        except BudgetDecisionDenied as exc:
            raise BudgetDecisionError(
                "BUDGET-DECISION-FORBIDDEN",
                str(exc),
                403,
            ) from exc
        return self._repository.decide(command, principal)
