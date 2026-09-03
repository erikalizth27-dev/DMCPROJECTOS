from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol

from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.enums import EstadoSiniestro
from siniestro_facil.domain.identity import AuthenticatedPrincipal
from siniestro_facil.domain.inspection_budget import (
    BudgetStatus,
    budget_valid_until,
)


class BudgetSubmissionError(ValueError):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


@dataclass(frozen=True, slots=True)
class SubmitBudgetCommand:
    claim_id: int
    inspection_id: int
    diagnosis: str
    presented_on: date
    expected_version: int
    idempotency_key: str = "budget-synthetic-0001"
    fingerprint: str = "0" * 64


@dataclass(frozen=True, slots=True)
class SubmittedBudget:
    id: int
    claim_id: int
    inspection_id: int
    provider_id: int
    diagnosis: str
    valid_from: date
    valid_until: date
    status: BudgetStatus
    current_state: EstadoSiniestro
    version: int


class BudgetSubmissionRepository(Protocol):
    def submit(
        self,
        command: SubmitBudgetCommand,
        principal: AuthenticatedPrincipal,
    ) -> SubmittedBudget: ...

    def get(
        self,
        claim_id: int,
        budget_id: int,
        principal: AuthenticatedPrincipal,
    ) -> SubmittedBudget | None: ...


class InMemoryBudgetSubmissionRepository:
    def __init__(self) -> None:
        self._rows: dict[int, SubmittedBudget] = {}
        self._next_id = 1
        self._requests: dict[str, tuple[str, SubmittedBudget]] = {}

    def submit(
        self,
        command: SubmitBudgetCommand,
        principal: AuthenticatedPrincipal,
    ) -> SubmittedBudget:
        existing = self._requests.get(command.idempotency_key)
        if existing is not None:
            fingerprint, result = existing
            if fingerprint == command.fingerprint:
                return result
            raise BudgetSubmissionError(
                "IDEMPOTENCY-CONFLICT",
                "Idempotency-Key ya fue utilizada con otro contenido",
                409,
            )
        row = SubmittedBudget(
            id=self._next_id,
            claim_id=command.claim_id,
            inspection_id=command.inspection_id,
            provider_id=1,
            diagnosis=command.diagnosis.strip(),
            valid_from=command.presented_on,
            valid_until=budget_valid_until(command.presented_on),
            status=BudgetStatus.RECEIVED,
            current_state=EstadoSiniestro.PRESUPUESTO_RECIBIDO,
            version=command.expected_version + 1,
        )
        self._rows[row.id] = row
        self._requests[command.idempotency_key] = (
            command.fingerprint,
            row,
        )
        self._next_id += 1
        return row

    def get(
        self,
        claim_id: int,
        budget_id: int,
        principal: AuthenticatedPrincipal,
    ) -> SubmittedBudget | None:
        row = self._rows.get(budget_id)
        return row if row is not None and row.claim_id == claim_id else None


class SubmitBudgetService:
    def __init__(self, repository: BudgetSubmissionRepository) -> None:
        self._repository = repository

    def execute(
        self,
        command: SubmitBudgetCommand,
        principal: AuthenticatedPrincipal,
    ) -> SubmittedBudget:
        if principal.role is not PrincipalRole.TALLER:
            raise BudgetSubmissionError(
                "BUDGET-FORBIDDEN",
                "Solo un taller autorizado puede presentar presupuestos",
                403,
            )
        if (
            command.claim_id <= 0
            or command.inspection_id <= 0
            or command.expected_version < 0
        ):
            raise BudgetSubmissionError(
                "BUDGET-REQUEST-INVALID",
                "Siniestro, inspección o versión inválidos",
                422,
            )
        if not (16 <= len(command.idempotency_key) <= 128):
            raise BudgetSubmissionError(
                "IDEMPOTENCY-KEY-INVALID",
                "Idempotency-Key debe tener entre 16 y 128 caracteres",
                422,
            )
        if len(command.fingerprint) != 64:
            raise BudgetSubmissionError(
                "BUDGET-FINGERPRINT-INVALID",
                "La huella de la solicitud es inválida",
                422,
            )
        if not command.diagnosis.strip():
            raise BudgetSubmissionError(
                "BUDGET-DIAGNOSIS-REQUIRED",
                "El diagnóstico es obligatorio",
                422,
            )
        return self._repository.submit(command, principal)


class GetBudgetService:
    def __init__(self, repository: BudgetSubmissionRepository) -> None:
        self._repository = repository

    def execute(
        self,
        claim_id: int,
        budget_id: int,
        principal: AuthenticatedPrincipal,
    ) -> SubmittedBudget:
        result = self._repository.get(claim_id, budget_id, principal)
        if result is None:
            raise BudgetSubmissionError(
                "BUDGET-NOT-FOUND",
                "Presupuesto no encontrado",
                404,
            )
        return result
