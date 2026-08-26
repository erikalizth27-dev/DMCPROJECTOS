from datetime import datetime, timedelta, timezone
import unittest

from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import (
    ActorType,
    TokenClaimsError,
    validate_verified_claims,
)


NOW = datetime(2026, 8, 25, 12, 0, tzinfo=timezone.utc)
ISSUER = "https://identity.example.invalid"
AUDIENCE = "siniestro-facil-backend"


def valid_claims() -> dict[str, object]:
    return {
        "iss": ISSUER,
        "aud": AUDIENCE,
        "sub": "user-syn-001",
        "iat": int((NOW - timedelta(minutes=5)).timestamp()),
        "exp": int((NOW + timedelta(minutes=55)).timestamp()),
        "auth_time": int((NOW - timedelta(minutes=10)).timestamp()),
        "actor_type": "interno",
        "role": "operador",
        "tenant_id": "tenant-syn-001",
    }


class IdentityClaimsTest(unittest.TestCase):
    def validate(self, claims: dict[str, object]):
        return validate_verified_claims(
            claims,
            expected_issuer=ISSUER,
            expected_audience=AUDIENCE,
            now=NOW,
        )

    def test_accepts_complete_verified_claims(self) -> None:
        principal = self.validate(valid_claims())
        self.assertEqual(PrincipalRole.OPERADOR, principal.role)
        self.assertEqual(ActorType.INTERNO, principal.actor_type)

    def test_rejects_wrong_issuer(self) -> None:
        claims = valid_claims()
        claims["iss"] = "https://other.example.invalid"
        with self.assertRaisesRegex(TokenClaimsError, "Emisor"):
            self.validate(claims)

    def test_accepts_expected_audience_in_list(self) -> None:
        claims = valid_claims()
        claims["aud"] = ["another-api", AUDIENCE]
        self.validate(claims)

    def test_rejects_wrong_audience(self) -> None:
        claims = valid_claims()
        claims["aud"] = "another-api"
        with self.assertRaisesRegex(TokenClaimsError, "Audiencia"):
            self.validate(claims)

    def test_rejects_expired_token(self) -> None:
        claims = valid_claims()
        claims["exp"] = int((NOW - timedelta(seconds=1)).timestamp())
        with self.assertRaisesRegex(TokenClaimsError, "vencido"):
            self.validate(claims)

    def test_rejects_unknown_role(self) -> None:
        claims = valid_claims()
        claims["role"] = "administrador_total"
        with self.assertRaisesRegex(TokenClaimsError, "Rol desconocido"):
            self.validate(claims)

    def test_rejects_unknown_actor_type(self) -> None:
        claims = valid_claims()
        claims["actor_type"] = "robot"
        with self.assertRaisesRegex(TokenClaimsError, "Tipo de actor"):
            self.validate(claims)

    def test_rejects_missing_subject(self) -> None:
        claims = valid_claims()
        claims.pop("sub")
        with self.assertRaisesRegex(TokenClaimsError, "sub"):
            self.validate(claims)

    def test_rejects_future_authentication_time(self) -> None:
        claims = valid_claims()
        claims["auth_time"] = int((NOW + timedelta(minutes=1)).timestamp())
        with self.assertRaisesRegex(TokenClaimsError, "fechas futuras"):
            self.validate(claims)


if __name__ == "__main__":
    unittest.main()
