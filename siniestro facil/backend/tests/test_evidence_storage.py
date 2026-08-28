from hashlib import sha256
from uuid import UUID

import pytest

from siniestro_facil.infrastructure.evidence_storage import (
    APPROVED_BUCKET,
    EvidenceStorageConfig,
    EvidenceStorageError,
    InMemoryEvidenceStorage,
    build_original_object_name,
    calculate_sha256,
)


EVIDENCE_ID = UUID("00000000-0000-4000-8000-000000000001")


def test_approved_configuration_is_valid() -> None:
    EvidenceStorageConfig().validate()


def test_rejects_bucket_outside_approved_decision() -> None:
    with pytest.raises(EvidenceStorageError, match="Bucket"):
        EvidenceStorageConfig(bucket="otro-bucket").validate()


def test_rejects_retention_lock_during_sprint_two() -> None:
    with pytest.raises(EvidenceStorageError, match="Retention lock"):
        EvidenceStorageConfig(retention_lock_enabled=True).validate()


def test_builds_unique_original_object_namespace() -> None:
    name = build_original_object_name(
        claim_id=42,
        evidence_id=EVIDENCE_ID,
        extension=".JPG",
    )
    assert name == (
        "siniestros/42/originales/"
        "00000000-0000-4000-8000-000000000001.jpg"
    )


def test_calculates_sha256_without_accepting_empty_content() -> None:
    content = b"evidencia sintetica"
    assert calculate_sha256(content) == sha256(content).hexdigest()
    with pytest.raises(EvidenceStorageError, match="vacía"):
        calculate_sha256(b"")


def test_stores_original_with_gs_uri_and_generation() -> None:
    storage = InMemoryEvidenceStorage()
    name = build_original_object_name(
        claim_id=42,
        evidence_id=EVIDENCE_ID,
        extension="jpg",
    )
    stored = storage.store_original(
        object_name=name,
        content=b"evidencia sintetica",
    )
    assert stored.bucket == APPROVED_BUCKET
    assert stored.uri == f"gs://{APPROVED_BUCKET}/{name}"
    assert stored.generation == 1
    assert stored.size == len(b"evidencia sintetica")


def test_original_cannot_be_overwritten() -> None:
    storage = InMemoryEvidenceStorage()
    name = build_original_object_name(
        claim_id=42,
        evidence_id=EVIDENCE_ID,
        extension="jpg",
    )
    storage.store_original(
        object_name=name,
        content=b"original",
    )
    with pytest.raises(EvidenceStorageError, match="sobrescribirse"):
        storage.store_original(
            object_name=name,
            content=b"reemplazo",
        )
