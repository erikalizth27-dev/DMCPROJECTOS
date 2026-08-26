from __future__ import annotations

import hashlib
import json


def fingerprint_request(payload: object) -> str:
    """Genera una huella estable para comparar reintentos idempotentes."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_idempotency_key(value: str) -> str:
    normalized = value.strip()
    if not 16 <= len(normalized) <= 128:
        raise ValueError("Idempotency-Key debe tener entre 16 y 128 caracteres")
    return normalized

