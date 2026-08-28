from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Protocol

from siniestro_facil.domain.authorization import (
    Action,
    AuthorizationDenied,
    authorize,
)
from siniestro_facil.domain.enums import EstadoSiniestro
from siniestro_facil.domain.identity import AuthenticatedPrincipal
from siniestro_facil.infrastructure.policy_adapter import PolicyLookup


class CoverageVerificationError(RuntimeError):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


@dataclass(frozen=True, slots=True)
class VerifyCoverageCommand:
    claim_id: int
    expected_version: int


@dataclass(frozen=True, slots=True)
class CoverageContext:
    claim_id: int
    policy_number: str
    document_number: str | None
    plate: str
    event_date: date
    current_state: EstadoSiniestro
    version: int


@dataclass(frozen=True, slots=True)
class CoverageVerification:
    claim_id: int
    active: bool
    deductible: Decimal
    validation_status: str
    current_state: EstadoSiniestro
    version: int
    human_review_required: bool


class CoverageRepository(Protocol):
    def find_context(
        self,
        claim_id: int,
        principal: AuthenticatedPrincipal,
    ) -> CoverageContext | None: ...

    def save_verification(
        self,
        context: CoverageContext,
        verification: CoverageVerification,
        principal: AuthenticatedPrincipal,
    ) -> CoverageVerification: ...


class VerifyCoverageService:
    def __init__(
        self,
        policies: PolicyLookup,
        repository: CoverageRepository,
    ) -> None:
        self._policies = policies
        self._repository = repository

    def execute(
        self,
        command: VerifyCoverageCommand,
        principal: AuthenticatedPrincipal,
    ) -> CoverageVerification:
        try:
            authorize(
                principal.role,
                Action.CAMBIAR_ESTADO,
                resource_in_scope=True,
            )
        except AuthorizationDenied as exc:
            raise CoverageVerificationError(
                "ACTION-NOT-ALLOWED",
                "Acción no permitida para el rol",
                403,
            ) from exc

        context = self._repository.find_context(command.claim_id, principal)
        if context is None:
            raise CoverageVerificationError(
                "CLAIM-NOT-FOUND",
                "Siniestro no encontrado",
                404,
            )
        if context.version != command.expected_version:
            raise CoverageVerificationError(
                "STATE-VERSION-CONFLICT",
                "La versión del siniestro está desactualizada",
                409,
            )
        if context.current_state is not EstadoSiniestro.REPORTADO:
            raise CoverageVerificationError(
                "INVALID-COVERAGE-STATE",
                "La cobertura sólo puede verificarse desde el estado reportado",
                409,
            )

        policy = self._policies.find(
            numero_poliza=context.policy_number,
            numero_documento=context.document_number,
        )
        if policy is None or policy.placa.strip().upper() != context.plate.strip().upper():
            raise CoverageVerificationError(
                "POLICY-NOT-ELIGIBLE",
                "No fue posible validar la póliza y el vehículo",
                422,
            )

        active = policy.is_active_on(context.event_date)
        verification = CoverageVerification(
            claim_id=context.claim_id,
            active=active,
            deductible=policy.deducible,
            validation_status="activa" if active else "requiere_revision",
            current_state=EstadoSiniestro.VALIDANDO_COBERTURA,
            version=context.version + 1,
            human_review_required=not active,
        )
        return self._repository.save_verification(
            context,
            verification,
            principal,
        )


class InMemoryCoverageRepository:
    def __init__(self, contexts: list[CoverageContext]) -> None:
        self._contexts = {context.claim_id: context for context in contexts}
        self.saved: list[CoverageVerification] = []

    def find_context(
        self,
        claim_id: int,
        principal: AuthenticatedPrincipal,
    ) -> CoverageContext | None:
        del principal
        return self._contexts.get(claim_id)

    def save_verification(
        self,
        context: CoverageContext,
        verification: CoverageVerification,
        principal: AuthenticatedPrincipal,
    ) -> CoverageVerification:
        del principal
        self._contexts[context.claim_id] = CoverageContext(
            claim_id=context.claim_id,
            policy_number=context.policy_number,
            document_number=context.document_number,
            plate=context.plate,
            event_date=context.event_date,
            current_state=verification.current_state,
            version=verification.version,
        )
        self.saved.append(verification)
        return verification
