import unittest

from siniestro_facil.domain.enums import EstadoSiniestro, RolUsuario
from siniestro_facil.domain.state_machine import (
    SolicitudTransicion,
    TransicionNoPermitida,
    validar_transicion,
)


class StateMachineTest(unittest.TestCase):
    def test_allows_normal_transition(self) -> None:
        validar_transicion(
            SolicitudTransicion(
                origen=EstadoSiniestro.REPORTADO,
                destino=EstadoSiniestro.VALIDANDO_COBERTURA,
                rol=RolUsuario.OPERADOR,
                motivo="Inicio de validacion",
            )
        )

    def test_reject_requires_human_confirmation(self) -> None:
        with self.assertRaisesRegex(TransicionNoPermitida, "confirmacion humana"):
            validar_transicion(
                SolicitudTransicion(
                    origen=EstadoSiniestro.EN_EVALUACION,
                    destino=EstadoSiniestro.RECHAZADO,
                    rol=RolUsuario.AJUSTADOR,
                    motivo="Cobertura no aplicable",
                )
            )

    def test_only_supervisor_reopens_rejection(self) -> None:
        with self.assertRaisesRegex(TransicionNoPermitida, "Solo un supervisor"):
            validar_transicion(
                SolicitudTransicion(
                    origen=EstadoSiniestro.RECHAZADO,
                    destino=EstadoSiniestro.EN_EVALUACION,
                    rol=RolUsuario.OPERADOR,
                    motivo="Nueva evidencia",
                )
            )

    def test_supervisor_can_reopen_rejection(self) -> None:
        validar_transicion(
            SolicitudTransicion(
                origen=EstadoSiniestro.RECHAZADO,
                destino=EstadoSiniestro.EN_EVALUACION,
                rol=RolUsuario.SUPERVISOR,
                motivo="Nueva evidencia",
            )
        )

    def test_evidence_checklist_is_required(self) -> None:
        with self.assertRaisesRegex(TransicionNoPermitida, "checklist"):
            validar_transicion(
                SolicitudTransicion(
                    origen=EstadoSiniestro.EVIDENCIA_PENDIENTE,
                    destino=EstadoSiniestro.EN_EVALUACION,
                    rol=RolUsuario.OPERADOR,
                    motivo="Continuar evaluacion",
                )
            )


if __name__ == "__main__":
    unittest.main()

