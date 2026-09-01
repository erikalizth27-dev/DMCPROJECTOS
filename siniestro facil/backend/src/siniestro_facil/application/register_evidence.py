from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from siniestro_facil.domain.authorization import (
    Action,
    AuthorizationDenied,
    authorize,
)
from siniestro_facil.domain.idempotency import (
    fingerprint_request,
    validate_idempotency_key,
)
from siniestro_facil.domain.identity import AuthenticatedPrincipal
from siniestro_facil.infrastructure.evidence_storage import APPROVED_BUCKET


class EvidenceRegistrationError(RuntimeError):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


@dataclass(frozen=True, slots=True)
class RegisterEvidenceCommand:
    claim_id: int
    evidence_type: str
    original_uri: str
    sha256_hex: str
    captured_at: datetime | None
    source: str | None
    derived_from_id: int | None
    metadata: dict[str, object]


@dataclass(frozen=True, slots=True)
class RegisteredEvidence:
    id: int
    claim_id: int
    evidence_type: str
    original_uri: str
    sha256_hex: str
    received_at: datetime
    derived_from_id: int | None


@dataclass(frozen=True, slots=True)
class StoredEvidenceRequest:
    fingerprint: str
    result: RegisteredEvidence


class EvidenceRepository(Protocol):
    def find_request(
        self,
        idempotency_key: str,
        principal: AuthenticatedPrincipal,
    ) -> StoredEvidenceRequest | None: ...

    def create(
        self,
        command: RegisterEvidenceCommand,
        principal: AuthenticatedPrincipal,
        *,
        idempotency_key: str,
        fingerprint: str,
    ) -> RegisteredEvidence: ...


class RegisterEvidenceService:
    def __init__(self, repository: EvidenceRepository) -> None:
        self._repository = repository

    def execute(
        self,
        command: RegisterEvidenceCommand,
        principal: AuthenticatedPrincipal,
        *,
        idempotency_key: str,
        request_payload: object,
    ) -> RegisteredEvidence:
        try:
            authorize(
                principal.role,
                Action.ADJUNTAR_EVIDENCIA,
                resource_in_scope=True,
            )
        except AuthorizationDenied as exc:
            raise EvidenceRegistrationError(
                "ACTION-NOT-ALLOWED",
                "Acción no permitida para el rol",
                403,
            ) from exc

        try:
            key = validate_idempotency_key(idempotency_key)
        except ValueError as exc:
            raise EvidenceRegistrationError(
                "IDEMPOTENCY-INVALID",
                str(exc),
                422,
            ) from exc

        uri_prefix = f"gs://{APPROVED_BUCKET}/siniestros/{command.claim_id}/"
        if not command.original_uri.startswith(uri_prefix):
            raise EvidenceRegistrationError(
                "EVIDENCE-URI-INVALID",
                "La evidencia no pertenece al bucket y siniestro aprobados",
                422,
            )
        digest = command.sha256_hex.strip().lower()
        if len(digest) != 64 or any(
            character not in "0123456789abcdef"
            for character in digest
        ):
            raise EvidenceRegistrationError(
                "EVIDENCE-HASH-INVALID",
                "El hash debe ser SHA-256 hexadecimal",
                422,
            )

        fingerprint = fingerprint_request(request_payload)
        stored = self._repository.find_request(key, principal)
        if stored is not None:
            if stored.fingerprint != fingerprint:
                raise EvidenceRegistrationError(
                    "IDEMPOTENCY-CONFLICT",
                    "Idempotency-Key ya fue utilizada con otro contenido",
                    409,
                )
            return stored.result

        normalized = RegisterEvidenceCommand(
            claim_id=command.claim_id,
            evidence_type=command.evidence_type.strip(),
            original_uri=command.original_uri,
            sha256_hex=digest,
            captured_at=command.captured_at,
            source=command.source.strip() if command.source else None,
            derived_from_id=command.derived_from_id,
            metadata=command.metadata,
        )
        return self._repository.create(
            normalized,
            principal,
            idempotency_key=key,
            fingerprint=fingerprint,
        )
