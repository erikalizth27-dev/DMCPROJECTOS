from datetime import datetime, timedelta, timezone

import pytest

from siniestro_facil.application.detect_case_relations import (
    CandidateCaseFacts,
    CaseRelationError,
    DetectCaseRelationsCommand,
    DetectCaseRelationsService,
    InMemoryCaseRelationRepository,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.fraud import RelationCriterion
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal


def principal(role=PrincipalRole.INVESTIGADOR_FRAUDE):
    now = datetime.now(timezone.utc)
    return AuthenticatedPrincipal(
        subject=f"{role.value}-relations",
        role=role,
        actor_type=ActorType.INTERNO,
        tenant_id="tenant-synthetic",
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


def execute(
    own,
    candidate,
    *,
    candidate_id=7,
    key="case-relation-detection-0001",
    role=PrincipalRole.INVESTIGADOR_FRAUDE,
    repository=None,
):
    repo = repository or InMemoryCaseRelationRepository()
    service = DetectCaseRelationsService(repo)
    payload = {
        "valores": {k.value: v for k, v in own.items()},
        "candidatos": [
            {
                "siniestroId": candidate_id,
                "valores": {k.value: v for k, v in candidate.items()},
            }
        ],
    }
    result = service.execute(
        DetectCaseRelationsCommand(
            claim_id=42,
            own_values=own,
            candidates=(CandidateCaseFacts(candidate_id, candidate),),
        ),
        principal(role),
        idempotency_key=key,
        request_payload=payload,
    )
    return result, repo


def test_exact_normalized_value_creates_candidate() -> None:
    result, _ = execute(
        {RelationCriterion.TELEFONO: " 809 555 0101 "},
        {RelationCriterion.TELEFONO: "809 555 0101"},
    )
    assert len(result.relations) == 1
    assert result.relations[0].normalized_value == "809 555 0101"
    assert result.relations[0].review_status == "pendiente_revision"


def test_unicode_and_case_are_normalized() -> None:
    result, _ = execute(
        {RelationCriterion.PERSONA: "José Pérez"},
        {RelationCriterion.PERSONA: "JOSÉ   PÉREZ"},
    )
    assert len(result.relations) == 1


def test_different_values_do_not_match() -> None:
    result, _ = execute(
        {RelationCriterion.TELEFONO: "8095550101"},
        {RelationCriterion.TELEFONO: "8095550102"},
    )
    assert result.relations == ()


def test_missing_value_is_not_inferred() -> None:
    result, _ = execute(
        {RelationCriterion.TALLER: "Taller Uno"},
        {RelationCriterion.TALLER: None},
    )
    assert result.relations == ()


def test_blank_value_is_not_inferred() -> None:
    result, _ = execute(
        {RelationCriterion.TALLER: "Taller Uno"},
        {RelationCriterion.TALLER: "   "},
    )
    assert result.relations == ()


def test_pair_is_canonical_and_never_merged() -> None:
    result, _ = execute(
        {RelationCriterion.ACCIDENTE: "A-100"},
        {RelationCriterion.ACCIDENTE: "A-100"},
        candidate_id=3,
    )
    relation = result.relations[0]
    assert (relation.claim_a, relation.claim_b) == (3, 42)
    assert relation.review_status == "pendiente_revision"


def test_same_claim_is_ignored() -> None:
    result, _ = execute(
        {RelationCriterion.ACCIDENTE: "A-100"},
        {RelationCriterion.ACCIDENTE: "A-100"},
        candidate_id=42,
    )
    assert result.relations == ()


def test_repetition_is_idempotent() -> None:
    repository = InMemoryCaseRelationRepository()
    first, _ = execute(
        {RelationCriterion.TALLER: "Taller Uno"},
        {RelationCriterion.TALLER: "taller uno"},
        repository=repository,
    )
    repeated, _ = execute(
        {RelationCriterion.TALLER: "Taller Uno"},
        {RelationCriterion.TALLER: "taller uno"},
        repository=repository,
    )
    assert repeated == first


def test_changed_content_conflicts() -> None:
    repository = InMemoryCaseRelationRepository()
    execute(
        {RelationCriterion.TALLER: "Taller Uno"},
        {RelationCriterion.TALLER: "Taller Uno"},
        repository=repository,
    )
    with pytest.raises(CaseRelationError) as error:
        execute(
            {RelationCriterion.TALLER: "Taller Uno"},
            {RelationCriterion.TALLER: "Taller Dos"},
            repository=repository,
        )
    assert error.value.code == "IDEMPOTENCY-CONFLICT"


def test_operator_cannot_detect_relations() -> None:
    with pytest.raises(CaseRelationError) as error:
        execute(
            {RelationCriterion.PERSONA: "Persona"},
            {RelationCriterion.PERSONA: "Persona"},
            role=PrincipalRole.OPERADOR,
        )
    assert error.value.code == "CASE-RELATION-FORBIDDEN"
