from datetime import datetime

import pytest

from siniestro_facil.infrastructure.evidence_upload import (
    EvidenceUploadError,
    EvidenceUploadService,
    MAX_EVIDENCE_BYTES,
)


class FakeBlob:
    def generate_signed_url(self, **kwargs):
        assert kwargs["version"] == "v4"
        assert kwargs["method"] == "PUT"
        assert kwargs["content_type"] == "image/png"
        assert isinstance(kwargs["expiration"], datetime)
        return "https://storage.example/upload"


class FakeBucket:
    def blob(self, object_name):
        assert object_name.startswith("siniestros/42/originales/")
        assert object_name.endswith(".png")
        return FakeBlob()


class FakeStorageClient:
    def bucket(self, bucket_name):
        assert bucket_name == "evidence-bucket"
        return FakeBucket()


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
    assert result.original_uri.startswith(
        "gs://evidence-bucket/siniestros/42/originales/"
    )
    assert result.content_type == "image/png"
