from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import google.auth
from google.auth.transport.requests import Request
from google.cloud import storage


ALLOWED_CONTENT_TYPES = {
    "image/jpeg": {".jpg", ".jpeg"},
    "image/png": {".png"},
    "application/pdf": {".pdf"},
}
MAX_EVIDENCE_BYTES = 10 * 1024 * 1024


class EvidenceUploadError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


@dataclass(frozen=True, slots=True)
class SignedEvidenceUpload:
    upload_url: str
    original_uri: str
    expires_at: datetime
    content_type: str


class EvidenceUploadService:
    def __init__(
        self,
        bucket_name: str,
        expiration_minutes: int = 15,
        storage_client: storage.Client | None = None,
    ) -> None:
        self._bucket_name = bucket_name
        self._expiration_minutes = expiration_minutes
        self._client = storage_client or storage.Client()

    def create_signed_upload(
        self,
        claim_id: int,
        filename: str,
        content_type: str,
        size_bytes: int,
    ) -> SignedEvidenceUpload:
        suffix = Path(filename).suffix.lower()
        allowed_suffixes = ALLOWED_CONTENT_TYPES.get(content_type)
        if allowed_suffixes is None or suffix not in allowed_suffixes:
            raise EvidenceUploadError(
                "EVIDENCE-TYPE-NOT-ALLOWED",
                "Solo se permiten archivos JPG, PNG o PDF.",
            )
        if size_bytes < 1 or size_bytes > MAX_EVIDENCE_BYTES:
            raise EvidenceUploadError(
                "EVIDENCE-SIZE-NOT-ALLOWED",
                "El archivo debe tener un tamaño máximo de 10 MB.",
            )

        object_name = (
            f"siniestros/{claim_id}/originales/{uuid4().hex}{suffix}"
        )
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=self._expiration_minutes
        )
        credentials, _ = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        credentials.refresh(Request())
        service_account_email = getattr(
            credentials,
            "service_account_email",
            None,
        )
        if not service_account_email or not credentials.token:
            raise EvidenceUploadError(
                "EVIDENCE-SIGNING-NOT-AVAILABLE",
                "No fue posible autorizar la carga de evidencia.",
                503,
            )

        blob = self._client.bucket(self._bucket_name).blob(object_name)
        upload_url = blob.generate_signed_url(
            version="v4",
            expiration=expires_at,
            method="PUT",
            content_type=content_type,
            credentials=credentials,
            service_account_email=service_account_email,
            access_token=credentials.token,
        )
        return SignedEvidenceUpload(
            upload_url=upload_url,
            original_uri=f"gs://{self._bucket_name}/{object_name}",
            expires_at=expires_at,
            content_type=content_type,
        )
