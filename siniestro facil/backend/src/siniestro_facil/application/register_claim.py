from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from siniestro_facil.domain.idempotency import fingerprint_request, validate_idempotency_key
from siniestro_facil.infrastructure.policy_adapter import PolicyLookup, PolicySnapshot


@dataclass(frozen=True, slots=True)
class RegisterClaimCommand:
    numero_poliza: str | None
    numero_documento: str | None
    placa: str
    fecha_evento: datetime
    ubicacion_evento: str
    tipo_evento: str
    medio_contacto: str


@dataclass(frozen=True, slots=True)
class RegisteredClaim:
    id: int
    estado_actual: str
    fecha_evento: datetime
    tipo_evento: str
    siguiente_paso: str


@dataclass(frozen=True, slots=True)
class StoredRequest:
    fingerprint: str
    result: RegisteredClaim


class ClaimRepository(Protocol):
    def find_request(self, idempotency_key: str) -> StoredRequest | None: ...

    def create(
        self,
        command: RegisterClaimCommand,
        policy: PolicySnapshot,
        *,
        idempotency_key: str,
        fingerprint: str,
    ) -> RegisteredClaim: ...


class ClaimRegistrationError(Exception):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class RegisterClaimService:
    def __init__(self, policies: PolicyLookup, repository: ClaimRepository) -> None:
        self._policies = policies
        self._repository = repository

    def execute(
        self,
        command: RegisterClaimCommand,
        *,
        idempotency_key: str,
        request_payload: object,
    ) -> RegisteredClaim:
        try:
            key = validate_idempotency_key(idempotency_key)
        except ValueError as exc:
            raise ClaimRegistrationError("IDEMPOTENCY-INVALID", str(exc), 422) from exc

        fingerprint = fingerprint_request(request_payload)
        stored = self._repository.find_request(key)
        if stored is not None:
            if stored.fingerprint != fingerprint:
                raise ClaimRegistrationError(
                    "IDEMPOTENCY-CONFLICT",
                    "Idempotency-Key ya fue utilizada con otro contenido",
                    409,
                )
            return stored.result

        policy = self._policies.find(
            numero_poliza=command.numero_poliza,
            numero_documento=command.numero_documento,
        )
        if policy is None:
            raise ClaimRegistrationError(
                "POLICY-NOT-ELIGIBLE",
                "No fue posible validar una póliza elegible",
                422,
            )
        if policy.placa.strip().upper() != command.placa.strip().upper():
            raise ClaimRegistrationError(
                "VEHICLE-NOT-COVERED",
                "La placa no corresponde a la póliza validada",
                422,
            )
        if not policy.is_active_on(command.fecha_evento.date()):
            raise ClaimRegistrationError(
                "COVERAGE-NOT-ACTIVE",
                "La cobertura no está vigente para la fecha del evento",
                422,
            )

        return self._repository.create(
            command,
            policy,
            idempotency_key=key,
            fingerprint=fingerprint,
        )


class InMemoryClaimRepository:
    """Repositorio de desarrollo; será sustituido por PostgreSQL en este incremento."""

    def __init__(self) -> None:
        self._requests: dict[str, StoredRequest] = {}
        self._next_id = 1

    def find_request(self, idempotency_key: str) -> StoredRequest | None:
        return self._requests.get(idempotency_key)

    def create(
        self,
        command: RegisterClaimCommand,
        policy: PolicySnapshot,
        *,
        idempotency_key: str,
        fingerprint: str,
    ) -> RegisteredClaim:
        del policy
        result = RegisteredClaim(
            id=self._next_id,
            estado_actual="reportado",
            fecha_evento=command.fecha_evento,
            tipo_evento=command.tipo_evento,
            siguiente_paso="validar_cobertura",
        )
        self._next_id += 1
        self._requests[idempotency_key] = StoredRequest(fingerprint, result)
        return result
