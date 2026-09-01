from datetime import datetime, timedelta, timezone

import pytest

from siniestro_facil.application.change_claim_state import (
    ChangeClaimStateCommand,
    ChangedClaimState,
    ChangeClaimStateService,
    ClaimStateChangeError,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.enums import EstadoSiniestro
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal


class StateRepository:
    def __init__(self, visible: bool = True) -> None:
        self.visible = visible
        self.received = None

    def change_state(self, command, principal):
        self.received = (command, principal)
        if not self.visible:
            return None
        return ChangedClaimState(
            id=command.claim_id,
            current_state=command.target_state,
            version=command.expected_version + 1,
        )


def principal(role: PrincipalRole = PrincipalRole.OPERADOR) -> AuthenticatedPrincipal:
    now = datetime.now(timezone.utc)
    return AuthenticatedPrincipal(
        subject="operator-synthetic",
        role=role,
        actor_type=ActorType.INTERNO,
        tenant_id="tenant-synthetic",
        issued_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(hours=1),
        authenticated_at=now - timedelta(minutes=1),
    )


def command(reason: str = "Iniciar validación") -> ChangeClaimStateCommand:
    return ChangeClaimStateCommand(
        claim_id=42,
        target_state=EstadoSiniestro.VALIDANDO_COBERTURA,
        reason=reason,
        expected_version=0,
    )


def test_changes_state_and_returns_incremented_version() -> None:
    repository = StateRepository()
    result = ChangeClaimStateService(repository).execute(command(), principal())
    assert result.id == 42
    assert result.current_state is EstadoSiniestro.VALIDANDO_COBERTURA
    assert result.version == 1
    assert repository.received is not None


def test_denies_role_without_change_permission() -> None:
    with pytest.raises(ClaimStateChangeError) as error:
        ChangeClaimStateService(StateRepository()).execute(
            command(),
            principal(PrincipalRole.ASEGURADO),
        )
    assert error.value.code == "ACTION-NOT-ALLOWED"
    assert error.value.status_code == 403


def test_hides_missing_or_out_of_scope_claim() -> None:
    with pytest.raises(ClaimStateChangeError) as error:
        ChangeClaimStateService(StateRepository(visible=False)).execute(
            command(),
            principal(),
        )
    assert error.value.code == "CLAIM-NOT-FOUND"
    assert error.value.status_code == 404


def test_rejects_blank_reason_before_repository_call() -> None:
    repository = StateRepository()
    with pytest.raises(ClaimStateChangeError) as error:
        ChangeClaimStateService(repository).execute(command("   "), principal())
    assert error.value.code == "INVALID-TRANSITION"
    assert repository.received is None
