from datetime import datetime, timedelta, timezone

import pytest

from siniestro_facil.application.register_evidence import (
    EvidenceRegistrationError,
    RegisterEvidenceCommand,
    RegisterEvidenceService,
    RegisteredEvidence,
    StoredEvidenceRequest,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import (
    ActorType,
    AuthenticatedPrincipal,
)
from siniestro_facil.infrastructure.evidence_storage import APPROVED_BUCKET


DIGEST = "a" * 64
URI = (
    f"gs://{APPROVED_BUCKET}/"
    "siniestros/42/originales/evidencia-sintetica.jpg"
)


class EvidenceRepository:
    def __init__(self) -> None:
        self.stored = None
        self.created = []

    def find_request(self, idempotency_key, principal):
        del idempotency_key, principal
        return self.stored

    def create(
        self,
        command,
        principal,
        *,
        idempotency_key,
        fingerprint,
    ):
        del principal, idempotency_key
        result = RegisteredEvidence(
            id=7,
            claim_id=command.claim_id,
            evidence_type=command.evidence_type,
            original_uri=command.original_uri,
            sha256_hex=command.sha256_hex,
            received_at=datetime.now(timezone.utc),
            derived_from_id=command.derived_from_id,
        )
        self.created.append((command, fingerprint))
        return result


def principal(
    role: PrincipalRole = PrincipalRole.ASEGURADO,
) -> AuthenticatedPrincipal:
    now = datetime.now(timezone.utc)
    return AuthenticatedPrincipal(
        subject="insured-synthetic",
        role=role,
        actor_type=ActorType.EXTERNO,
        tenant_id="tenant-synthetic",
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


def command(
    *,
    uri: str = URI,
    digest: str = DIGEST,
) -> RegisterEvidenceCommand:
    return RegisterEvidenceCommand(
        claim_id=42,
        evidence_type="fotografia",
        original_uri=uri,
        sha256_hex=digest,
        captured_at=None,
        source="asegurado",
        derived_from_id=None,
        metadata={"generation": "1"},
    )


def payload(uri: str = URI, digest: str = DIGEST):
    return {
        "tipoEvidencia": "fotografia",
        "contenidoOriginalUri": uri,
        "hash": digest,
    }


def test_registers_evidence_with_approved_uri_and_sha256() -> None:
    repository = EvidenceRepository()
    result = RegisterEvidenceService(repository).execute(
        command(),
        principal(),
        idempotency_key="evidence-idem-0001",
        request_payload=payload(),
    )
    assert result.id == 7
    assert result.sha256_hex == DIGEST
    assert len(repository.created) == 1


def test_replays_same_idempotent_request() -> None:
    repository = EvidenceRepository()
    service = RegisterEvidenceService(repository)
    first = service.execute(
        command(),
        principal(),
        idempotency_key="evidence-idem-0001",
        request_payload=payload(),
    )
    fingerprint = repository.created[0][1]
    repository.stored = StoredEvidenceRequest(fingerprint, first)
    replay = service.execute(
        command(),
        principal(),
        idempotency_key="evidence-idem-0001",
        request_payload=payload(),
    )
    assert replay == first
    assert len(repository.created) == 1


def test_rejects_idempotency_key_reused_with_other_content() -> None:
    repository = EvidenceRepository()
    repository.stored = StoredEvidenceRequest("different", RegisteredEvidence(
        id=7,
        claim_id=42,
        evidence_type="fotografia",
        original_uri=URI,
        sha256_hex=DIGEST,
        received_at=datetime.now(timezone.utc),
        derived_from_id=None,
    ))
    with pytest.raises(EvidenceRegistrationError) as error:
        RegisterEvidenceService(repository).execute(
            command(),
            principal(),
            idempotency_key="evidence-idem-0001",
            request_payload=payload(),
        )
    assert error.value.code == "IDEMPOTENCY-CONFLICT"


def test_rejects_uri_outside_approved_claim_prefix() -> None:
    with pytest.raises(EvidenceRegistrationError) as error:
        RegisterEvidenceService(EvidenceRepository()).execute(
            command(uri=f"gs://{APPROVED_BUCKET}/siniestros/99/file.jpg"),
            principal(),
            idempotency_key="evidence-idem-0001",
            request_payload=payload(),
        )
    assert error.value.code == "EVIDENCE-URI-INVALID"


def test_rejects_non_sha256_hash() -> None:
    with pytest.raises(EvidenceRegistrationError) as error:
        RegisterEvidenceService(EvidenceRepository()).execute(
            command(digest="not-a-sha256"),
            principal(),
            idempotency_key="evidence-idem-0001",
            request_payload=payload(),
        )
    assert error.value.code == "EVIDENCE-HASH-INVALID"


def test_denies_role_without_evidence_permission() -> None:
    with pytest.raises(EvidenceRegistrationError) as error:
        RegisterEvidenceService(EvidenceRepository()).execute(
            command(),
            principal(PrincipalRole.INVESTIGADOR_FRAUDE),
            idempotency_key="evidence-idem-0001",
            request_payload=payload(),
        )
    assert error.value.code == "ACTION-NOT-ALLOWED"
    assert error.value.status_code == 403
