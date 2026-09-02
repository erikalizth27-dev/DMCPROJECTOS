from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

from siniestro_facil.application.assistance_contracts import AssistanceRecord
from siniestro_facil.domain.assistance import (
    AssistanceStatus,
    InvalidAssistanceTransition,
    ProviderResult,
    validate_assistance_transition,
)
from siniestro_facil.domain.authorization import (
    Action,
    AuthorizationDenied,
    authorize,
)
from siniestro_facil.domain.identity import AuthenticatedPrincipal


MAX_PILOT_ATTEMPTS = 3


class AssistanceManagementError(RuntimeError):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


@dataclass(frozen=True, slots=True)
class RegisterProviderReplyCommand:
    claim_id: int
    assistance_id: int
    result: ProviderResult
    expected_attempt: int
    external_reference: str | None = None


@dataclass(frozen=True, slots=True)
class ReassignAssistanceCommand:
    claim_id: int
    assistance_id: int
    new_provider_id: int
    expected_attempt: int
    reason: str


class AssistanceManagementRepository(Protocol):
    def register_reply(
        self,
        command: RegisterProviderReplyCommand,
        principal: AuthenticatedPrincipal,
    ) -> AssistanceRecord: ...

    def reassign(
        self,
        command: ReassignAssistanceCommand,
        principal: AuthenticatedPrincipal,
    ) -> AssistanceRecord: ...


class InMemoryAssistanceManagementRepository:
    def __init__(
        self,
        records: list[AssistanceRecord],
        *,
        visible_claim_ids: set[int],
    ) -> None:
        self._records = {record.id: record for record in records}
        self._visible = set(visible_claim_ids)
        self._next_id = max(self._records, default=0) + 1

    def _get(
        self,
        claim_id: int,
        assistance_id: int,
    ) -> AssistanceRecord:
        record = self._records.get(assistance_id)
        if (
            record is None
            or record.claim_id != claim_id
            or claim_id not in self._visible
        ):
            raise AssistanceManagementError(
                "ASSISTANCE-NOT-FOUND",
                "Asistencia no encontrada",
                404,
            )
        return record

    @staticmethod
    def _check_attempt(
        record: AssistanceRecord,
        expected_attempt: int,
    ) -> None:
        if record.attempt != expected_attempt:
            raise AssistanceManagementError(
                "ASSISTANCE-VERSION-CONFLICT",
                "La asistencia fue modificada por otra operación",
                409,
            )

    def register_reply(
        self,
        command: RegisterProviderReplyCommand,
        principal: AuthenticatedPrincipal,
    ) -> AssistanceRecord:
        del principal
        current = self._get(command.claim_id, command.assistance_id)
        self._check_attempt(current, command.expected_attempt)
        target = {
            ProviderResult.ACCEPTED: AssistanceStatus.ACCEPTED,
            ProviderResult.REJECTED: AssistanceStatus.REJECTED,
            ProviderResult.NO_RESPONSE: AssistanceStatus.NO_RESPONSE,
        }[command.result]
        try:
            validate_assistance_transition(current.status, target)
        except InvalidAssistanceTransition as exc:
            raise AssistanceManagementError(
                "ASSISTANCE-TRANSITION-INVALID",
                str(exc),
                409,
            ) from exc
        updated = AssistanceRecord(
            id=current.id,
            claim_id=current.claim_id,
            provider_id=current.provider_id,
            assistance_type=current.assistance_type,
            status=target,
            attempt=current.attempt,
            created_at=current.created_at,
            updated_at=datetime.now(timezone.utc),
        )
        self._records[current.id] = updated
        return updated

    def reassign(
        self,
        command: ReassignAssistanceCommand,
        principal: AuthenticatedPrincipal,
    ) -> AssistanceRecord:
        del principal
        current = self._get(command.claim_id, command.assistance_id)
        self._check_attempt(current, command.expected_attempt)
        if current.status not in {
            AssistanceStatus.REJECTED,
            AssistanceStatus.NO_RESPONSE,
        }:
            raise AssistanceManagementError(
                "ASSISTANCE-REASSIGNMENT-INVALID",
                "Solo se reasigna una solicitud rechazada o sin respuesta",
                409,
            )
        if current.attempt >= MAX_PILOT_ATTEMPTS:
            raise AssistanceManagementError(
                "RETRY-LIMIT-REACHED",
                "Se alcanzó el máximo de intentos del piloto",
                409,
            )
        if (
            command.new_provider_id <= 0
            or command.new_provider_id == current.provider_id
        ):
            raise AssistanceManagementError(
                "PROVIDER-INVALID",
                "El nuevo proveedor debe ser válido y diferente",
                422,
            )
        if not command.reason.strip():
            raise AssistanceManagementError(
                "REASSIGNMENT-REASON-REQUIRED",
                "El motivo de reasignación es obligatorio",
                422,
            )
        now = datetime.now(timezone.utc)
        replacement = AssistanceRecord(
            id=self._next_id,
            claim_id=current.claim_id,
            provider_id=command.new_provider_id,
            assistance_type=current.assistance_type,
            status=AssistanceStatus.PENDING,
            attempt=current.attempt + 1,
            created_at=now,
            updated_at=now,
        )
        self._next_id += 1
        self._records[replacement.id] = replacement
        return replacement


class RegisterProviderReplyService:
    def __init__(self, repository: AssistanceManagementRepository) -> None:
        self._repository = repository

    def execute(
        self,
        command: RegisterProviderReplyCommand,
        principal: AuthenticatedPrincipal,
    ) -> AssistanceRecord:
        try:
            authorize(
                principal.role,
                Action.SOLICITAR_ASISTENCIA,
                resource_in_scope=True,
            )
        except AuthorizationDenied as exc:
            raise AssistanceManagementError(
                "ACTION-NOT-ALLOWED",
                "Acción no permitida para el rol",
                403,
            ) from exc
        if command.expected_attempt <= 0:
            raise AssistanceManagementError(
                "ASSISTANCE-VERSION-INVALID",
                "El intento esperado debe ser mayor que cero",
                422,
            )
        return self._repository.register_reply(command, principal)


class ReassignAssistanceService:
    def __init__(self, repository: AssistanceManagementRepository) -> None:
        self._repository = repository

    def execute(
        self,
        command: ReassignAssistanceCommand,
        principal: AuthenticatedPrincipal,
    ) -> AssistanceRecord:
        try:
            authorize(
                principal.role,
                Action.SOLICITAR_ASISTENCIA,
                resource_in_scope=True,
            )
        except AuthorizationDenied as exc:
            raise AssistanceManagementError(
                "ACTION-NOT-ALLOWED",
                "Acción no permitida para el rol",
                403,
            ) from exc
        if command.expected_attempt <= 0:
            raise AssistanceManagementError(
                "ASSISTANCE-VERSION-INVALID",
                "El intento esperado debe ser mayor que cero",
                422,
            )
        return self._repository.reassign(command, principal)
