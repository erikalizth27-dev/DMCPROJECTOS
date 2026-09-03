from datetime import datetime, timezone
from decimal import Decimal

from fastapi.testclient import TestClient

from siniestro_facil.config import Settings
from siniestro_facil.domain.audit import TimelineEvent, project_timeline_event
from siniestro_facil.domain.authorization import (
    Action,
    AuthorizationDenied,
    PrincipalRole,
    authorize,
)
from siniestro_facil.infrastructure.payment_adapter import (
    DeterministicPaymentAdapter,
)
from siniestro_facil.main import create_app


def test_database_url_is_excluded_from_settings_representation() -> None:
    secret = "postgresql://user:super-secret@127.0.0.1/database"
    rendered = repr(Settings(database_url=secret))
    assert secret not in rendered
    assert "super-secret" not in rendered


def test_validation_response_does_not_echo_sensitive_input() -> None:
    response = TestClient(create_app()).post(
        "/api/v1/siniestros",
        json={
            "numeroPoliza": "POL-SYN-001",
            "placa": "SYN0001",
            "fechaEvento": datetime.now(timezone.utc).isoformat(),
            "ubicacionEvento": "Ubicación sintética",
            "tipoEvento": "colision",
            "medioContacto": "synthetic@example.invalid",
            "password": "never-expose-this-value",
        },
    )
    assert response.status_code == 422
    assert "never-expose-this-value" not in response.text
    assert response.json()["codigo"] == "VALIDATION-ERROR"


def test_validation_details_exclude_raw_input_and_context() -> None:
    response = TestClient(create_app()).post(
        "/api/v1/siniestros",
        json={"password": "another-secret-value"},
    )
    assert response.status_code == 422
    body = response.json()
    assert all("input" not in item for item in body["detalles"])
    assert all("ctx" not in item for item in body["detalles"])
    assert "another-secret-value" not in response.text


def test_validation_error_preserves_correlation_id() -> None:
    response = TestClient(create_app()).get(
        "/api/v1/indicadores/operativos",
        headers={"X-Correlation-ID": "s6-security-correlation"},
    )
    assert response.status_code == 422
    assert (
        response.json()["correlationId"]
        == "s6-security-correlation"
    )
    assert (
        response.headers["X-Correlation-ID"]
        == "s6-security-correlation"
    )


def test_only_supervisor_can_authorize_payment() -> None:
    for role in PrincipalRole:
        if role is PrincipalRole.SUPERVISOR:
            authorize(
                role,
                Action.AUTORIZAR_PAGO,
                resource_in_scope=True,
            )
        else:
            try:
                authorize(
                    role,
                    Action.AUTORIZAR_PAGO,
                    resource_in_scope=True,
                )
            except AuthorizationDenied:
                pass
            else:
                raise AssertionError(f"{role.value} autorizó un pago")


def test_sensitive_audit_detail_is_redacted_for_operator() -> None:
    event = TimelineEvent(
        event_id=1,
        claim_id=4,
        event_type="alerta_fraude_revisada",
        actor_id=3,
        detail={
            "explicacion": "reservada",
            "token": "never-return",
        },
        sensitive=True,
    )
    view = project_timeline_event(event, PrincipalRole.OPERADOR)
    assert view.detail == {
        "resumen": "Información sensible restringida"
    }
    assert "never-return" not in str(view.detail)


def test_payment_adapter_cannot_report_real_transfer() -> None:
    result = DeterministicPaymentAdapter(
        version="s6-security-validation"
    ).emit(payment_id=1, amount=Decimal("10.00"))
    assert result.simulated is True
    assert result.money_transferred is False
