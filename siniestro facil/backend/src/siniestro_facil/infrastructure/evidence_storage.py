from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from uuid import UUID


APPROVED_BUCKET = "project-77c17016-86bc-4fc4-a97-siniestro-evidencias"
APPROVED_REGION = "us-central1"


class EvidenceStorageError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class EvidenceStorageConfig:
    bucket: str = APPROVED_BUCKET
    region: str = APPROVED_REGION
    uniform_access: bool = True
    versioning_enabled: bool = True
    public_access_prevention: bool = True
    retention_lock_enabled: bool = False

    def validate(self) -> None:
        if self.bucket != APPROVED_BUCKET:
            raise EvidenceStorageError("Bucket fuera de S2-DEC-02")
        if self.region != APPROVED_REGION:
            raise EvidenceStorageError("Región fuera de S2-DEC-02")
        if not self.uniform_access or not self.versioning_enabled:
            raise EvidenceStorageError(
                "Acceso uniforme y versionado son obligatorios"
            )
        if not self.public_access_prevention:
            raise EvidenceStorageError("El acceso público debe estar impedido")
        if self.retention_lock_enabled:
            raise EvidenceStorageError(
                "Retention lock no está autorizado durante Sprint 2"
            )


@dataclass(frozen=True, slots=True)
class StoredEvidenceObject:
    bucket: str
    object_name: str
    uri: str
    sha256_hex: str
    size: int
    generation: int


def calculate_sha256(content: bytes) -> str:
    if not content:
        raise EvidenceStorageError("La evidencia no puede estar vacía")
    return sha256(content).hexdigest()


def build_original_object_name(
    *,
    claim_id: int,
    evidence_id: UUID,
    extension: str,
) -> str:
    if claim_id <= 0:
        raise EvidenceStorageError("El identificador del siniestro es inválido")
    normalized_extension = extension.strip().lower().lstrip(".")
    if not normalized_extension or not normalized_extension.isalnum():
        raise EvidenceStorageError("La extensión de evidencia es inválida")
    return (
        f"siniestros/{claim_id}/originales/"
        f"{evidence_id}.{normalized_extension}"
    )


class InMemoryEvidenceStorage:
    """Adaptador determinista que aplica las reglas aprobadas sin modificar GCP."""

    def __init__(self, config: EvidenceStorageConfig | None = None) -> None:
        self.config = config or EvidenceStorageConfig()
        self.config.validate()
        self._objects: dict[str, StoredEvidenceObject] = {}

    def store_original(
        self,
        *,
        object_name: str,
        content: bytes,
    ) -> StoredEvidenceObject:
        if object_name in self._objects:
            raise EvidenceStorageError(
                "El objeto original ya existe y no puede sobrescribirse"
            )
        digest = calculate_sha256(content)
        stored = StoredEvidenceObject(
            bucket=self.config.bucket,
            object_name=object_name,
            uri=f"gs://{self.config.bucket}/{object_name}",
            sha256_hex=digest,
            size=len(content),
            generation=1,
        )
        self._objects[object_name] = stored
        return stored

    def get(self, object_name: str) -> StoredEvidenceObject | None:
        return self._objects.get(object_name)
