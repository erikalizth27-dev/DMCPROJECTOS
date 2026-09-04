from __future__ import annotations

from typing import Annotated, Mapping

from fastapi import Header
from google.auth import exceptions as google_auth_exceptions
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from siniestro_facil.api.errors import BusinessError
from siniestro_facil.config import Settings
from siniestro_facil.domain.identity import (
    AuthenticatedPrincipal,
    TokenClaimsError,
    validate_verified_claims,
)


_GOOGLE_REQUEST = google_requests.Request()


def _bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise BusinessError(
            "AUTHENTICATION-REQUIRED",
            "Autenticación requerida",
            401,
        )
    scheme, separator, token = authorization.partition(" ")
    if separator != " " or scheme.lower() != "bearer" or not token.strip():
        raise BusinessError(
            "INVALID-AUTHORIZATION",
            "Credencial de autenticación inválida",
            401,
        )
    return token.strip()


def verify_identity_platform_token(
    token: str,
    settings: Settings,
) -> AuthenticatedPrincipal:
    errors = settings.identity_configuration_errors()
    if errors:
        raise BusinessError(
            "IDENTITY-NOT-CONFIGURED",
            "Servicio de identidad no configurado",
            503,
        )

    try:
        claims: Mapping[str, object] = id_token.verify_firebase_token(
            token,
            _GOOGLE_REQUEST,
            audience=settings.identity_audience,
        )
        return validate_verified_claims(
            claims,
            expected_issuer=settings.identity_issuer or "",
            expected_audience=settings.identity_audience or "",
        )
    except (
        ValueError,
        google_auth_exceptions.GoogleAuthError,
        TokenClaimsError,
    ) as error:
        raise BusinessError(
            "INVALID-IDENTITY-TOKEN",
            "Token de identidad inválido",
            401,
        ) from error


def get_authenticated_principal(
    authorization: Annotated[str | None, Header()] = None,
) -> AuthenticatedPrincipal:
    settings = Settings.from_environment()
    return verify_identity_platform_token(
        _bearer_token(authorization),
        settings,
    )
