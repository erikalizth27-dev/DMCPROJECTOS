from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from siniestro_facil.domain.authorization import (
    Action,
    AuthorizationDenied,
    authorize,
)
from siniestro_facil.domain.enums import EstadoSiniestro
from siniestro_facil.domain.identity import AuthenticatedPrincipal


class ClaimStateChangeError(RuntimeError):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


@dataclass(frozen=True, slots=True)
class ChangeClaimStateCommand:
    claim_id: int
    target_state: EstadoSiniestro
    reason: str
    expected_version: int
    evidence_complete: bool = False
    human_confirmation: bool = False


@dataclass(frozen=True, slots=True)
class ChangedClaimState:
    id: int
    current_state: EstadoSiniestro
    version: int


class ClaimStateRepository(Protocol):
    def change_state(
        self,
        command: ChangeClaimStateCommand,
        principal: AuthenticatedPrincipal,
    ) -> ChangedClaimState | None: ...


class ChangeClaimStateService:
    def __init__(self, repository: ClaimStateRepository) -> None:
        self._repository = repository

    def execute(
        self,
        command: ChangeClaimStateCommand,
        principal: AuthenticatedPrincipal,
    ) -> ChangedClaimState:
        if command.claim_id <= 0:
            raise ClaimStateChangeError(
                "CLAIM-NOT-FOUND",
                "Siniestro no encontrado",
                404,
            )
        if not command.reason.strip():
            raise ClaimStateChangeError(
                "INVALID-TRANSITION",
                "El motivo es obligatorio",
                409,
            )
        try:
            authorize(
                principal.role,
                Action.CAMBIAR_ESTADO,
                resource_in_scope=True,
            )
        except AuthorizationDenied as exc:
            raise ClaimStateChangeError(
                "ACTION-NOT-ALLOWED",
                "Acción no permitida para el rol",
                403,
            ) from exc

        result = self._repository.change_state(command, principal)
        if result is None:
            raise ClaimStateChangeError(
                "CLAIM-NOT-FOUND",
                "Siniestro no encontrado",
                404,
            )
        return result
