import inspect
from datetime import date, datetime, timezone
from types import SimpleNamespace

from siniestro_facil.domain.inspection_budget import BudgetStatus
from siniestro_facil.persistence.inspection_budget_repository import (
    PostgreSQLInspectionBudgetRepository,
)


def test_repository_maps_inspection_without_extra_attributes() -> None:
    row = SimpleNamespace(
        id_inspeccion=7,
        id_siniestro=41,
        fecha_programada=datetime(2026, 9, 3, tzinfo=timezone.utc),
    )

    record = PostgreSQLInspectionBudgetRepository._inspection_record(row)

    assert record.id == 7
    assert record.claim_id == 41
    assert record.scheduled_at == row.fecha_programada


def test_repository_maps_existing_budget_columns() -> None:
    row = SimpleNamespace(
        id_presupuesto=8,
        id_siniestro=41,
        id_proveedor=3,
        diagnostico="Diagnóstico",
        vigencia_desde=date(2026, 9, 2),
        vigencia_hasta=date(2026, 9, 17),
        estado="recibido",
    )

    record = PostgreSQLInspectionBudgetRepository._budget_record(row)

    assert record.id == 8
    assert record.status is BudgetStatus.RECEIVED
    assert record.valid_until == date(2026, 9, 17)


def test_internal_scope_requires_active_assignment() -> None:
    source = inspect.getsource(
        PostgreSQLInspectionBudgetRepository._internal_identity_in_scope
    )

    assert "AsignacionSiniestro.id_siniestro == claim_id" in source
    assert "AsignacionSiniestro.finalizado_en.is_(None)" in source
    assert "PrincipalRole.SUPERVISOR" in source


def test_taller_scope_is_limited_to_its_provider() -> None:
    source = inspect.getsource(
        PostgreSQLInspectionBudgetRepository.find_budget
    )

    assert "PrincipalRole.TALLER" in source
    assert "row.id_proveedor != identity.id_proveedor" in source


def test_inspection_lookup_checks_claim_relation() -> None:
    source = inspect.getsource(
        PostgreSQLInspectionBudgetRepository.find_inspection
    )

    assert "row.id_siniestro != claim_id" in source
