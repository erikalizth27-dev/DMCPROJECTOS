from __future__ import annotations

import hashlib
import re

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import google.auth
from google.api_core.exceptions import NotFound
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
    upload_fields: dict[str, str]
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

    def validate_uploaded_object(
        self,
        claim_id: int,
        original_uri: str,
        sha256_hex: str,
    ) -> None:
        uri_prefix = f"gs://{self._bucket_name}/"
        object_prefix = f"siniestros/{claim_id}/originales/"

        if not original_uri.startswith(uri_prefix):
            raise EvidenceUploadError(
                "EVIDENCE-OBJECT-NOT-AUTHORIZED",
                "La ubicación de la evidencia no está autorizada.",
            )

        object_name = original_uri[len(uri_prefix):]
        object_suffix = object_name[len(object_prefix):]

        if (
            not object_name.startswith(object_prefix)
            or re.fullmatch(
                r"[0-9a-f]{32}\.(?:jpg|jpeg|png|pdf)",
                object_suffix,
            )
            is None
        ):
            raise EvidenceUploadError(
                "EVIDENCE-OBJECT-NOT-AUTHORIZED",
                "La evidencia no pertenece al siniestro indicado.",
            )

        blob = self._client.bucket(self._bucket_name).blob(object_name)
        try:
            blob.reload()
        except NotFound as exc:
            raise EvidenceUploadError(
                "EVIDENCE-OBJECT-NOT-FOUND",
                "El archivo cargado no fue encontrado.",
            ) from exc

        if not blob.size or blob.size > MAX_EVIDENCE_BYTES:
            raise EvidenceUploadError(
                "EVIDENCE-SIZE-NOT-ALLOWED",
                "El archivo debe tener un tamaño máximo de 10 MB.",
            )

        if blob.content_type not in ALLOWED_CONTENT_TYPES:
            raise EvidenceUploadError(
                "EVIDENCE-TYPE-NOT-ALLOWED",
                "Solo se permiten archivos JPG, PNG o PDF.",
            )

        contents = blob.download_as_bytes(
            if_generation_match=blob.generation,
        )
        actual_sha256 = hashlib.sha256(contents).hexdigest()

        if actual_sha256 != sha256_hex.lower():
            raise EvidenceUploadError(
                "EVIDENCE-HASH-MISMATCH",
                "El hash no coincide con el archivo cargado.",
            )

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

        policy = self._client.generate_signed_post_policy_v4(
            self._bucket_name,
            object_name,
            expiration=expires_at,
            conditions=[
                ["content-length-range", 1, MAX_EVIDENCE_BYTES],
                {"Content-Type": content_type},
                {"success_action_status": "204"},
            ],
            fields={
                "Content-Type": content_type,
                "success_action_status": "204",
            },
            credentials=credentials,
            service_account_email=service_account_email,
            access_token=credentials.token,
        )
        return SignedEvidenceUpload(
            upload_url=policy["url"],
            upload_fields=policy["fields"],
            original_uri=f"gs://{self._bucket_name}/{object_name}",
            expires_at=expires_at,
            content_type=content_type,
        )
