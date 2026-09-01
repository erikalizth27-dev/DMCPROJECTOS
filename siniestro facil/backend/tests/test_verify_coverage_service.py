from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from siniestro_facil.application.verify_coverage import (
    CoverageContext,
    CoverageVerificationError,
    InMemoryCoverageRepository,
    VerifyCoverageCommand,
    VerifyCoverageService,
)
from siniestro_facil.domain.authorization import PrincipalRole
from siniestro_facil.domain.enums import EstadoSiniestro
from siniestro_facil.domain.identity import ActorType, AuthenticatedPrincipal
from siniestro_facil.infrastructure.policy_adapter import (
    InMemoryPolicyAdapter,
    PolicySnapshot,
)


def principal(
    role: PrincipalRole = PrincipalRole.OPERADOR,
) -> AuthenticatedPrincipal:
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


def context(
    *,
    version: int = 0,
    state: EstadoSiniestro = EstadoSiniestro.REPORTADO,
) -> CoverageContext:
    return CoverageContext(
        claim_id=42,
        policy_number="POL-SYN-001",
        document_number="DOC-SYN-001",
        plate="SYN0001",
        event_date=date(2026, 8, 28),
        current_state=state,
        version=version,
    )


def policy(*, active: bool = True) -> PolicySnapshot:
    return PolicySnapshot(
        numero_poliza="POL-SYN-001",
        numero_documento="DOC-SYN-001",
        placa="SYN0001",
        vigente_desde=date(2026, 1, 1),
        vigente_hasta=date(2026, 12, 31),
        deducible=Decimal("500.00"),
        cobertura_activa=active,
    )


def service(
    *,
    active: bool = True,
    stored_context: CoverageContext | None = None,
):
    repository = InMemoryCoverageRepository(
        [stored_context or context()]
    )
    return (
        VerifyCoverageService(
            InMemoryPolicyAdapter([policy(active=active)]),
            repository,
        ),
        repository,
    )


def test_returns_active_coverage_and_deductible() -> None:
    use_case, repository = service()
    result = use_case.execute(
        VerifyCoverageCommand(claim_id=42, expected_version=0),
        principal(),
    )
    assert result.active is True
    assert result.deductible == Decimal("500.00")
    assert result.validation_status == "activa"
    assert result.current_state is EstadoSiniestro.VALIDANDO_COBERTURA
    assert result.version == 1
    assert result.human_review_required is False
    assert repository.saved == [result]


def test_inactive_coverage_requires_human_review_without_rejection() -> None:
    use_case, _ = service(active=False)
    result = use_case.execute(
        VerifyCoverageCommand(claim_id=42, expected_version=0),
        principal(),
    )
    assert result.active is False
    assert result.validation_status == "requiere_revision"
    assert result.human_review_required is True
    assert result.current_state is EstadoSiniestro.VALIDANDO_COBERTURA
    assert result.current_state is not EstadoSiniestro.RECHAZADO


def test_rejects_stale_version() -> None:
    use_case, _ = service(stored_context=context(version=2))
    with pytest.raises(CoverageVerificationError) as error:
        use_case.execute(
            VerifyCoverageCommand(claim_id=42, expected_version=1),
            principal(),
        )
    assert error.value.code == "STATE-VERSION-CONFLICT"
    assert error.value.status_code == 409


def test_requires_reported_state() -> None:
    use_case, _ = service(
        stored_context=context(
            state=EstadoSiniestro.VALIDANDO_COBERTURA,
        )
    )
    with pytest.raises(CoverageVerificationError) as error:
        use_case.execute(
            VerifyCoverageCommand(claim_id=42, expected_version=0),
            principal(),
        )
    assert error.value.code == "INVALID-COVERAGE-STATE"


def test_denies_role_without_state_change_permission() -> None:
    use_case, _ = service()
    with pytest.raises(CoverageVerificationError) as error:
        use_case.execute(
            VerifyCoverageCommand(claim_id=42, expected_version=0),
            principal(PrincipalRole.ASEGURADO),
        )
    assert error.value.code == "ACTION-NOT-ALLOWED"
    assert error.value.status_code == 403


def test_hides_missing_claim() -> None:
    repository = InMemoryCoverageRepository([])
    use_case = VerifyCoverageService(
        InMemoryPolicyAdapter([policy()]),
        repository,
    )
    with pytest.raises(CoverageVerificationError) as error:
        use_case.execute(
            VerifyCoverageCommand(claim_id=999, expected_version=0),
            principal(),
        )
    assert error.value.code == "CLAIM-NOT-FOUND"
    assert error.value.status_code == 404
