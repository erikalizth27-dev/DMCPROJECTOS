from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.enums import EstadoSiniestro
from siniestro_facil.domain.identity import AuthenticatedPrincipal


class InspectionSchedulingError(ValueError):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


@dataclass(frozen=True, slots=True)
class ScheduleInspectionCommand:
    claim_id: int
    scheduled_at: datetime
    expected_version: int
    reason: str


@dataclass(frozen=True, slots=True)
class ScheduledInspection:
    id: int
    claim_id: int
    scheduled_at: datetime
    current_state: EstadoSiniestro
    version: int


class InspectionSchedulingRepository(Protocol):
    def schedule(
        self,
        command: ScheduleInspectionCommand,
        principal: AuthenticatedPrincipal,
    ) -> ScheduledInspection: ...

    def get(
        self,
        claim_id: int,
        inspection_id: int,
        principal: AuthenticatedPrincipal,
    ) -> ScheduledInspection | None: ...


class InMemoryInspectionSchedulingRepository:
    def __init__(self) -> None:
        self._rows: dict[int, ScheduledInspection] = {}
        self._next_id = 1

    def schedule(
        self,
        command: ScheduleInspectionCommand,
        principal: AuthenticatedPrincipal,
    ) -> ScheduledInspection:
        row = ScheduledInspection(
            id=self._next_id,
            claim_id=command.claim_id,
            scheduled_at=command.scheduled_at,
            current_state=EstadoSiniestro.INSPECCION_PROGRAMADA,
            version=command.expected_version + 1,
        )
        self._rows[row.id] = row
        self._next_id += 1
        return row

    def get(
        self,
        claim_id: int,
        inspection_id: int,
        principal: AuthenticatedPrincipal,
    ) -> ScheduledInspection | None:
        row = self._rows.get(inspection_id)
        return row if row is not None and row.claim_id == claim_id else None


class ScheduleInspectionService:
    def __init__(self, repository: InspectionSchedulingRepository) -> None:
        self._repository = repository

    def execute(
        self,
        command: ScheduleInspectionCommand,
        principal: AuthenticatedPrincipal,
    ) -> ScheduledInspection:
        if principal.role not in {
            PrincipalRole.OPERADOR,
            PrincipalRole.AJUSTADOR,
        }:
            raise InspectionSchedulingError(
                "INSPECTION-FORBIDDEN",
                "Rol no autorizado para programar inspecciones",
                403,
            )
        if command.claim_id <= 0 or command.expected_version < 0:
            raise InspectionSchedulingError(
                "INSPECTION-REQUEST-INVALID",
                "Siniestro o versión inválidos",
                422,
            )
        if not command.reason.strip():
            raise InspectionSchedulingError(
                "INSPECTION-REASON-REQUIRED",
                "El motivo es obligatorio",
                422,
            )
        if command.scheduled_at.tzinfo is None:
            raise InspectionSchedulingError(
                "INSPECTION-DATETIME-INVALID",
                "La fecha programada debe incluir zona horaria",
                422,
            )
        return self._repository.schedule(command, principal)


class GetInspectionService:
    def __init__(self, repository: InspectionSchedulingRepository) -> None:
        self._repository = repository

    def execute(
        self,
        claim_id: int,
        inspection_id: int,
        principal: AuthenticatedPrincipal,
    ) -> ScheduledInspection:
        result = self._repository.get(
            claim_id,
            inspection_id,
            principal,
        )
        if result is None:
            raise InspectionSchedulingError(
                "INSPECTION-NOT-FOUND",
                "Inspección no encontrada",
                404,
            )
        return result
