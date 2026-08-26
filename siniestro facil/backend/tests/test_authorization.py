import unittest

from siniestro_facil.domain.authorization import (
    Action,
    AlertDetailLevel,
    AuthorizationDenied,
    PaymentApproval,
    PrincipalRole,
    alert_detail_level,
    authorize,
    validate_payment_approval,
)


class AuthorizationTest(unittest.TestCase):
    def test_insured_can_view_own_claim(self) -> None:
        authorize(PrincipalRole.ASEGURADO, Action.CONSULTAR_SINIESTRO, resource_in_scope=True)

    def test_insured_cannot_view_another_claim(self) -> None:
        with self.assertRaisesRegex(AuthorizationDenied, "fuera del alcance"):
            authorize(PrincipalRole.ASEGURADO, Action.CONSULTAR_SINIESTRO, resource_in_scope=False)

    def test_workshop_cannot_create_claim(self) -> None:
        with self.assertRaisesRegex(AuthorizationDenied, "no permitida"):
            authorize(PrincipalRole.TALLER, Action.CREAR_SINIESTRO, resource_in_scope=True)

    def test_insured_can_request_assistance_for_own_claim(self) -> None:
        authorize(PrincipalRole.ASEGURADO, Action.SOLICITAR_ASISTENCIA, resource_in_scope=True)

    def test_investigator_cannot_request_assistance(self) -> None:
        with self.assertRaisesRegex(AuthorizationDenied, "no permitida"):
            authorize(PrincipalRole.INVESTIGADOR_FRAUDE, Action.SOLICITAR_ASISTENCIA, resource_in_scope=True)

    def test_investigator_can_review_alert(self) -> None:
        authorize(PrincipalRole.INVESTIGADOR_FRAUDE, Action.REVISAR_ALERTA, resource_in_scope=True)

    def test_operator_receives_alert_summary(self) -> None:
        self.assertEqual(AlertDetailLevel.RESUMEN, alert_detail_level(PrincipalRole.OPERADOR))

    def test_investigator_receives_alert_detail(self) -> None:
        self.assertEqual(AlertDetailLevel.DETALLE, alert_detail_level(PrincipalRole.INVESTIGADOR_FRAUDE))

    def test_insured_cannot_read_alerts(self) -> None:
        with self.assertRaisesRegex(AuthorizationDenied, "no permitida"):
            alert_detail_level(PrincipalRole.ASEGURADO)

    def test_operator_cannot_authorize_payment(self) -> None:
        with self.assertRaises(AuthorizationDenied):
            authorize(PrincipalRole.OPERADOR, Action.AUTORIZAR_PAGO, resource_in_scope=True)

    def test_supervisor_can_access_out_of_scope_resource(self) -> None:
        authorize(PrincipalRole.SUPERVISOR, Action.CONSULTAR_AUDITORIA, resource_in_scope=False)

    def test_payment_requires_different_people(self) -> None:
        with self.assertRaisesRegex(AuthorizationDenied, "misma persona"):
            validate_payment_approval(PaymentApproval("user-1", "user-1", PrincipalRole.SUPERVISOR))

    def test_payment_requires_supervisor(self) -> None:
        with self.assertRaisesRegex(AuthorizationDenied, "supervisor"):
            validate_payment_approval(PaymentApproval("user-1", "user-2", PrincipalRole.AJUSTADOR))

    def test_payment_accepts_separation_of_duties(self) -> None:
        validate_payment_approval(PaymentApproval("user-1", "user-2", PrincipalRole.SUPERVISOR))


if __name__ == "__main__":
    unittest.main()
