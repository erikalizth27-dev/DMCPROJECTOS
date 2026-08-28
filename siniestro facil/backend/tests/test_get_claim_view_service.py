from datetime import datetime, timedelta, timezone

import pytest

from siniestro_facil.application.get_claim_view import (
    ClaimNotVisible,
    ClaimView,
    GetClaimViewService,
    NEXT_STEP_BY_STATE,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal


def principal(role: PrincipalRole) -> AuthenticatedPrincipal:
    now = datetime.now(timezone.utc)
    return AuthenticatedPrincipal(
        subject=f"subject-{role.value}",
        role=role,
        actor_type=(
            ActorType.EXTERNO
            if role is PrincipalRole.ASEGURADO
            else ActorType.INTERNO
        ),
        tenant_id="tenant-synthetic",
        issued_at=now - timedelta(minutes=5),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=5),
    )


class FakeRepository:
    def __init__(self, visible: bool = True) -> None:
        self.visible = visible

    def find_visible(self, claim_id, authenticated):
        if not self.visible:
            return None
        return ClaimView(
            id=claim_id,
            estado_actual="reportado",
            fecha_evento=datetime(2026, 8, 25, tzinfo=timezone.utc),
            tipo_evento="colision",
            siguiente_paso=NEXT_STEP_BY_STATE["reportado"],
        )


def test_returns_visible_claim_and_next_step() -> None:
    result = GetClaimViewService(FakeRepository()).execute(
        42, principal(PrincipalRole.ASEGURADO)
    )
    assert result.id == 42
    assert result.siguiente_paso == "validar_cobertura"


def test_hides_missing_and_out_of_scope_with_same_exception() -> None:
    service = GetClaimViewService(FakeRepository(visible=False))
    with pytest.raises(ClaimNotVisible, match="no encontrado"):
        service.execute(42, principal(PrincipalRole.ASEGURADO))


def test_closed_claim_has_no_next_step() -> None:
    assert NEXT_STEP_BY_STATE["cerrado"] is None
