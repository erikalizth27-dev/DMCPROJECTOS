from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol

from siniestro_facil.domain.authorization import (
    Action,
    AuthorizationDenied,
    authorize,
)
from siniestro_facil.domain.fraud import (
    RelationCriterion,
    canonical_claim_pair,
    normalize_exact_value,
)
from siniestro_facil.domain.idempotency import (
    fingerprint_request,
    validate_idempotency_key,
)
from siniestro_facil.domain.identity import AuthenticatedPrincipal


class CaseRelationError(RuntimeError):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


@dataclass(frozen=True, slots=True)
class CandidateCaseFacts:
    claim_id: int
    values: Mapping[RelationCriterion, str | None]


@dataclass(frozen=True, slots=True)
class DetectCaseRelationsCommand:
    claim_id: int
    own_values: Mapping[RelationCriterion, str | None]
    candidates: tuple[CandidateCaseFacts, ...]


@dataclass(frozen=True, slots=True)
class CaseRelationCandidate:
    id: int
    claim_a: int
    claim_b: int
    criterion: RelationCriterion
    normalized_value: str
    review_status: str = "pendiente_revision"


@dataclass(frozen=True, slots=True)
class CaseRelationResult:
    claim_id: int
    relations: tuple[CaseRelationCandidate, ...]


@dataclass(frozen=True, slots=True)
class StoredRelationRequest:
    fingerprint: str
    result: CaseRelationResult


class CaseRelationRepository(Protocol):
    def find_request(
        self, idempotency_key: str
    ) -> StoredRelationRequest | None: ...

    def create(
        self,
        claim_id: int,
        matches: tuple[
            tuple[int, int, RelationCriterion, str], ...
        ],
        principal: AuthenticatedPrincipal,
        *,
        idempotency_key: str,
        fingerprint: str,
    ) -> CaseRelationResult: ...


class InMemoryCaseRelationRepository:
    def __init__(self) -> None:
        self._next_id = 1
        self._requests: dict[str, StoredRelationRequest] = {}
        self._relations: dict[
            tuple[int, int, RelationCriterion], CaseRelationCandidate
        ] = {}

    def find_request(
        self, idempotency_key: str
    ) -> StoredRelationRequest | None:
        return self._requests.get(idempotency_key)

    def create(
        self,
        claim_id: int,
        matches: tuple[
            tuple[int, int, RelationCriterion, str], ...
        ],
        principal: AuthenticatedPrincipal,
        *,
        idempotency_key: str,
        fingerprint: str,
    ) -> CaseRelationResult:
        created: list[CaseRelationCandidate] = []
        for claim_a, claim_b, criterion, value in matches:
            key = (claim_a, claim_b, criterion)
            relation = self._relations.get(key)
            if relation is None:
                relation = CaseRelationCandidate(
                    id=self._next_id,
                    claim_a=claim_a,
                    claim_b=claim_b,
                    criterion=criterion,
                    normalized_value=value,
                )
                self._relations[key] = relation
                self._next_id += 1
            created.append(relation)
        result = CaseRelationResult(claim_id, tuple(created))
        self._requests[idempotency_key] = StoredRelationRequest(
            fingerprint, result
        )
        return result


class DetectCaseRelationsService:
    def __init__(self, repository: CaseRelationRepository) -> None:
        self._repository = repository

    def execute(
        self,
        command: DetectCaseRelationsCommand,
        principal: AuthenticatedPrincipal,
        *,
        idempotency_key: str,
        request_payload: object,
    ) -> CaseRelationResult:
        try:
            authorize(
                principal.role,
                Action.REVISAR_ALERTA,
                resource_in_scope=True,
            )
        except AuthorizationDenied as exc:
            raise CaseRelationError(
                "CASE-RELATION-FORBIDDEN",
                "Solo investigador o supervisor puede detectar relaciones",
                403,
            ) from exc
        if command.claim_id <= 0:
            raise CaseRelationError(
                "CASE-RELATION-INVALID",
                "El identificador del siniestro es inválido",
                422,
            )
        try:
            key = validate_idempotency_key(idempotency_key)
        except ValueError as exc:
            raise CaseRelationError(
                "IDEMPOTENCY-INVALID", str(exc), 422
            ) from exc
        fingerprint = fingerprint_request(request_payload)
        existing = self._repository.find_request(key)
        if existing is not None:
            if existing.fingerprint != fingerprint:
                raise CaseRelationError(
                    "IDEMPOTENCY-CONFLICT",
                    "Idempotency-Key ya fue utilizada con otro contenido",
                    409,
                )
            return existing.result

        normalized_own = self._normalized_present(command.own_values)
        matches: set[tuple[int, int, RelationCriterion, str]] = set()
        for candidate in command.candidates:
            if candidate.claim_id <= 0:
                raise CaseRelationError(
                    "CASE-RELATION-INVALID",
                    "Candidato con identificador inválido",
                    422,
                )
            if candidate.claim_id == command.claim_id:
                continue
            normalized_candidate = self._normalized_present(
                candidate.values
            )
            for criterion, value in normalized_own.items():
                if normalized_candidate.get(criterion) != value:
                    continue
                claim_a, claim_b = canonical_claim_pair(
                    command.claim_id, candidate.claim_id
                )
                matches.add((claim_a, claim_b, criterion, value))
        ordered = tuple(
            sorted(
                matches,
                key=lambda item: (
                    item[0], item[1], item[2].value, item[3]
                ),
            )
        )
        return self._repository.create(
            command.claim_id,
            ordered,
            principal,
            idempotency_key=key,
            fingerprint=fingerprint,
        )

    @staticmethod
    def _normalized_present(
        values: Mapping[RelationCriterion, str | None],
    ) -> dict[RelationCriterion, str]:
        normalized: dict[RelationCriterion, str] = {}
        for criterion, value in values.items():
            if value is None or not value.strip():
                continue
            normalized[criterion] = normalize_exact_value(value)
        return normalized
