from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from siniestro_facil.api.auth import (
    _bearer_token,
    verify_identity_platform_token,
)
from siniestro_facil.api.errors import BusinessError
from siniestro_facil.config import Settings
from siniestro_facil.domain.authorization import PrincipalRole


NOW = datetime.now(timezone.utc)
PROJECT_ID = "project-77c17016-86bc-4fc4-a97"
ISSUER = f"https://securetoken.google.com/{PROJECT_ID}"


def settings() -> Settings:
    return Settings(
        identity_issuer=ISSUER,
        identity_audience=PROJECT_ID,
    )


def claims() -> dict[str, object]:
    return {
        "iss": ISSUER,
        "aud": PROJECT_ID,
        "sub": "identity-user-001",
        "iat": int((NOW - timedelta(minutes=1)).timestamp()),
        "exp": int((NOW + timedelta(minutes=30)).timestamp()),
        "auth_time": int((NOW - timedelta(minutes=2)).timestamp()),
        "actor_type": "externo",
        "role": "asegurado",
        "tenant_id": "seguro-horizonte",
    }


def test_extracts_bearer_token() -> None:
    assert _bearer_token("Bearer token-value") == "token-value"


@pytest.mark.parametrize("header", [None, "", "Basic abc", "Bearer "])
def test_rejects_missing_or_invalid_authorization(header: str | None) -> None:
    with pytest.raises(BusinessError) as captured:
        _bearer_token(header)
    assert captured.value.status_code == 401


def test_verifies_firebase_signature_before_mapping_claims() -> None:
    with patch(
        "siniestro_facil.api.auth.id_token.verify_firebase_token",
        return_value=claims(),
    ) as verifier:
        principal = verify_identity_platform_token("signed-token", settings())

    verifier.assert_called_once()
    assert principal.role is PrincipalRole.ASEGURADO
    assert principal.tenant_id == "seguro-horizonte"


def test_rejects_invalid_signature_without_leaking_details() -> None:
    with patch(
        "siniestro_facil.api.auth.id_token.verify_firebase_token",
        side_effect=ValueError("signature details"),
    ):
        with pytest.raises(BusinessError) as captured:
            verify_identity_platform_token("invalid-token", settings())

    assert captured.value.code == "INVALID-IDENTITY-TOKEN"
    assert captured.value.status_code == 401
    assert "signature" not in captured.value.message


def test_requires_identity_configuration() -> None:
    with pytest.raises(BusinessError) as captured:
        verify_identity_platform_token("token", Settings())

    assert captured.value.code == "IDENTITY-NOT-CONFIGURED"
    assert captured.value.status_code == 503
