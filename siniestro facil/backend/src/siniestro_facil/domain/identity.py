from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Mapping

from siniestro_facil.domain.authorization import PrincipalRole


class ActorType(StrEnum):
    EXTERNO = "externo"
    INTERNO = "interno"
    PROVEEDOR = "proveedor"


class TokenClaimsError(PermissionError):
    """Los claims verificados no cumplen el contrato de identidad."""


@dataclass(frozen=True, slots=True)
class AuthenticatedPrincipal:
    subject: str
    role: PrincipalRole
    actor_type: ActorType
    tenant_id: str
    issued_at: datetime
    expires_at: datetime
    authenticated_at: datetime


def _required_text(claims: Mapping[str, object], name: str) -> str:
    value = claims.get(name)
    if not isinstance(value, str) or not value.strip():
        raise TokenClaimsError(f"Claim obligatorio inválido: {name}")
    return value


def _timestamp(claims: Mapping[str, object], name: str) -> datetime:
    value = claims.get(name)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TokenClaimsError(f"Claim temporal inválido: {name}")
    return datetime.fromtimestamp(value, tz=timezone.utc)


def validate_verified_claims(
    claims: Mapping[str, object],
    *,
    expected_issuer: str,
    expected_audience: str,
    now: datetime | None = None,
) -> AuthenticatedPrincipal:
    """Valida claims de un JWT cuya firma ya verificó el adaptador de identidad."""
    current_time = now or datetime.now(timezone.utc)
    if current_time.tzinfo is None:
        raise ValueError("now debe incluir zona horaria")

    issuer = _required_text(claims, "iss")
    if issuer != expected_issuer:
        raise TokenClaimsError("Emisor de token inválido")

    audience = claims.get("aud")
    audiences = {audience} if isinstance(audience, str) else set(audience or [])
    if expected_audience not in audiences:
        raise TokenClaimsError("Audiencia de token inválida")

    issued_at = _timestamp(claims, "iat")
    expires_at = _timestamp(claims, "exp")
    authenticated_at = _timestamp(claims, "auth_time")
    if expires_at <= current_time:
        raise TokenClaimsError("Token vencido")
    if issued_at > current_time or authenticated_at > current_time:
        raise TokenClaimsError("Token contiene fechas futuras")

    try:
        role = PrincipalRole(_required_text(claims, "role"))
    except ValueError as error:
        raise TokenClaimsError("Rol desconocido") from error

    try:
        actor_type = ActorType(_required_text(claims, "actor_type"))
    except ValueError as error:
        raise TokenClaimsError("Tipo de actor desconocido") from error

    return AuthenticatedPrincipal(
        subject=_required_text(claims, "sub"),
        role=role,
        actor_type=actor_type,
        tenant_id=_required_text(claims, "tenant_id"),
        issued_at=issued_at,
        expires_at=expires_at,
        authenticated_at=authenticated_at,
    )
