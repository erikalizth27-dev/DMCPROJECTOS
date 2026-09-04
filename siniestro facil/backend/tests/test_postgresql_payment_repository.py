import inspect

from siniestro_facil.persistence.payment_repository import (
    PostgreSQLPaymentRepository,
)


def prepare_source() -> str:
    return inspect.getsource(PostgreSQLPaymentRepository.prepare)


def authorize_source() -> str:
    return inspect.getsource(PostgreSQLPaymentRepository.authorize)


def test_prepare_uses_single_transaction_and_locks_claim() -> None:
    source = prepare_source()
    assert "with self._factory() as session, session.begin()" in source
    assert "with_for_update=True" in source
    assert "Pago(" in source


def test_prepare_requires_linked_identity_and_assignment() -> None:
    source = prepare_source()
    assert "self._identity(session, principal)" in source
    assert "self._can_prepare(" in source
    assert '"PAYMENT-NOT-FOUND"' in source


def test_prepare_persists_audit_and_idempotency() -> None:
    source = prepare_source()
    assert 'tipo_evento="pago_preparado"' in source
    assert "SolicitudPreparacionPagoIdempotente(" in source
    assert '"transferencia_realizada": False' in source


def test_authorization_locks_payment_and_checks_version() -> None:
    source = authorize_source()
    assert ".with_for_update()" in source
    assert "row.version != payment.version" in source
    assert '"PAYMENT-VERSION-CONFLICT"' in source


def test_authorization_enforces_supervisor_and_separation() -> None:
    source = authorize_source()
    assert "PrincipalRole.SUPERVISOR" in source
    assert "row.id_usuario_prepara == identity.id_usuario" in source
    assert '"PAYMENT-AUTHORIZE-FORBIDDEN"' in source


def test_authorization_rechecks_critical_alert_atomically() -> None:
    source = authorize_source()
    assert 'Alerta.severidad == "critica"' in source
    assert 'Alerta.estado_revision == "pendiente"' in source
    assert '"PAYMENT-BLOCKED-BY-CRITICAL-ALERT"' in source


def test_authorization_persists_formal_audit_and_idempotency() -> None:
    source = authorize_source()
    assert "authorization = Autorizacion(" in source
    assert 'tipo_evento="pago_autorizado"' in source
    assert "SolicitudAutorizacionPagoIdempotente(" in source
    assert '"transferencia_realizada": False' in source
