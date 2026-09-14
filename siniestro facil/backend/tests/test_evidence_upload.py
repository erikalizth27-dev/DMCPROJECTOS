import hashlib
from datetime import datetime

import pytest

from siniestro_facil.infrastructure.evidence_upload import (
    EvidenceUploadError,
    EvidenceUploadService,
    MAX_EVIDENCE_BYTES,
)


class FakeStorageClient:
    def generate_signed_post_policy_v4(
        self,
        bucket_name,
        object_name,
        **kwargs,
    ):
        assert bucket_name == "evidence-bucket"
        assert object_name.startswith("siniestros/42/originales/")
        assert object_name.endswith(".png")
        assert ["content-length-range", 1, MAX_EVIDENCE_BYTES] in kwargs["conditions"]
        assert {"Content-Type": "image/png"} in kwargs["conditions"]
        return {
            "url": "https://storage.example/upload",
            "fields": {
                "key": object_name,
                "Content-Type": "image/png",
                "policy": "signed-policy",
            },
        }

class FakeCredentials:
    service_account_email = "backend@example.iam.gserviceaccount.com"
    token = "access-token"

    def refresh(self, _request):
        return None


def test_rejects_unsupported_extension_before_signing():
    service = EvidenceUploadService("evidence-bucket", storage_client=FakeStorageClient())

    with pytest.raises(EvidenceUploadError) as exc:
        service.create_signed_upload(42, "evidencia.exe", "image/png", 100)

    assert exc.value.code == "EVIDENCE-TYPE-NOT-ALLOWED"


def test_rejects_file_larger_than_ten_megabytes():
    service = EvidenceUploadService("evidence-bucket", storage_client=FakeStorageClient())

    with pytest.raises(EvidenceUploadError) as exc:
        service.create_signed_upload(
            42,
            "evidencia.pdf",
            "application/pdf",
            MAX_EVIDENCE_BYTES + 1,
        )

    assert exc.value.code == "EVIDENCE-SIZE-NOT-ALLOWED"


def test_creates_unique_signed_upload(monkeypatch):
    monkeypatch.setattr(
        "siniestro_facil.infrastructure.evidence_upload.google.auth.default",
        lambda scopes: (FakeCredentials(), "test-project"),
    )
    service = EvidenceUploadService(
        "evidence-bucket",
        expiration_minutes=15,
        storage_client=FakeStorageClient(),
    )

    result = service.create_signed_upload(42, "foto.png", "image/png", 1024)

    assert result.upload_url == "https://storage.example/upload"
    assert result.upload_fields["policy"] == "signed-policy"
    assert result.upload_fields["Content-Type"] == "image/png"
    assert result.original_uri.startswith(
        "gs://evidence-bucket/siniestros/42/originales/"
    )
    assert result.content_type == "image/png"

class FakeStoredBlob:
    def __init__(self, contents=b"evidencia-segura", content_type="image/png"):
        self.contents = contents
        self.size = len(contents)
        self.content_type = content_type
        self.generation = 7

    def reload(self):
        return None

    def download_as_bytes(self, **kwargs):
        assert kwargs["if_generation_match"] == 7
        return self.contents


class FakeValidationBucket:
    def __init__(self, blob):
        self.stored_blob = blob

    def blob(self, object_name):
        assert object_name.startswith("siniestros/42/originales/")
        return self.stored_blob


class FakeValidationClient:
    def __init__(self, blob):
        self.stored_blob = blob

    def bucket(self, bucket_name):
        assert bucket_name == "evidence-bucket"
        return FakeValidationBucket(self.stored_blob)


def test_validates_uploaded_object_and_hash():
    contents = b"evidencia-segura"
    service = EvidenceUploadService(
        "evidence-bucket",
        storage_client=FakeValidationClient(FakeStoredBlob(contents)),
    )
    uri = "gs://evidence-bucket/siniestros/42/originales/" + ("a" * 32) + ".png"

    service.validate_uploaded_object(
        42,
        uri,
        hashlib.sha256(contents).hexdigest(),
    )


def test_rejects_object_from_another_claim():
    service = EvidenceUploadService(
        "evidence-bucket",
        storage_client=FakeValidationClient(FakeStoredBlob()),
    )
    uri = "gs://evidence-bucket/siniestros/99/originales/" + ("a" * 32) + ".png"

    with pytest.raises(EvidenceUploadError) as exc:
        service.validate_uploaded_object(42, uri, "0" * 64)

    assert exc.value.code == "EVIDENCE-OBJECT-NOT-AUTHORIZED"


def test_rejects_hash_that_does_not_match_uploaded_object():
    service = EvidenceUploadService(
        "evidence-bucket",
        storage_client=FakeValidationClient(FakeStoredBlob()),
    )
    uri = "gs://evidence-bucket/siniestros/42/originales/" + ("a" * 32) + ".png"

    with pytest.raises(EvidenceUploadError) as exc:
        service.validate_uploaded_object(42, uri, "0" * 64)

    assert exc.value.code == "EVIDENCE-HASH-MISMATCH"
