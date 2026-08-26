from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PrincipalRole(StrEnum):
    ASEGURADO = "asegurado"
    OPERADOR = "operador"
    AJUSTADOR = "ajustador"
    TALLER = "taller"
    INVESTIGADOR_FRAUDE = "investigador_fraude"
    SUPERVISOR = "supervisor"


class Action(StrEnum):
    CREAR_SINIESTRO = "crear_siniestro"
    CONSULTAR_SINIESTRO = "consultar_siniestro"
    ADJUNTAR_EVIDENCIA = "adjuntar_evidencia"
    CAMBIAR_ESTADO = "cambiar_estado"
    SOLICITAR_ASISTENCIA = "solicitar_asistencia"
    REGISTRAR_PRESUPUESTO = "registrar_presupuesto"
    CONSULTAR_ALERTA_RESUMEN = "consultar_alerta_resumen"
    REVISAR_ALERTA = "revisar_alerta"
    CONSULTAR_INFORMACION_AMPLIADA = "consultar_informacion_ampliada"
    PREPARAR_PAGO = "preparar_pago"
    AUTORIZAR_PAGO = "autorizar_pago"
    REABRIR_RECHAZO = "reabrir_rechazo"
    CONFIRMAR_ENTREGA = "confirmar_entrega"
    CONSULTAR_AUDITORIA = "consultar_auditoria"
    CONFIGURAR_POLITICA_FRAUDE = "configurar_politica_fraude"


ROLE_PERMISSIONS: dict[PrincipalRole, frozenset[Action]] = {
    PrincipalRole.ASEGURADO: frozenset(
        {
            Action.CREAR_SINIESTRO,
            Action.CONSULTAR_SINIESTRO,
            Action.ADJUNTAR_EVIDENCIA,
            Action.SOLICITAR_ASISTENCIA,
            Action.CONFIRMAR_ENTREGA,
            Action.CONSULTAR_AUDITORIA,
        }
    ),
    PrincipalRole.OPERADOR: frozenset(
        {
            Action.CREAR_SINIESTRO,
            Action.CONSULTAR_SINIESTRO,
            Action.ADJUNTAR_EVIDENCIA,
            Action.CAMBIAR_ESTADO,
            Action.SOLICITAR_ASISTENCIA,
            Action.CONSULTAR_ALERTA_RESUMEN,
            Action.PREPARAR_PAGO,
            Action.CONSULTAR_AUDITORIA,
        }
    ),
    PrincipalRole.AJUSTADOR: frozenset(
        {
            Action.CONSULTAR_SINIESTRO,
            Action.ADJUNTAR_EVIDENCIA,
            Action.CAMBIAR_ESTADO,
            Action.SOLICITAR_ASISTENCIA,
            Action.CONSULTAR_ALERTA_RESUMEN,
            Action.PREPARAR_PAGO,
            Action.CONSULTAR_AUDITORIA,
        }
    ),
    PrincipalRole.TALLER: frozenset(
        {
            Action.CONSULTAR_SINIESTRO,
            Action.ADJUNTAR_EVIDENCIA,
            Action.CAMBIAR_ESTADO,
            Action.REGISTRAR_PRESUPUESTO,
            Action.CONSULTAR_AUDITORIA,
        }
    ),
    PrincipalRole.INVESTIGADOR_FRAUDE: frozenset(
        {
            Action.CONSULTAR_SINIESTRO,
            Action.ADJUNTAR_EVIDENCIA,
            Action.CONSULTAR_ALERTA_RESUMEN,
            Action.REVISAR_ALERTA,
            Action.CONSULTAR_INFORMACION_AMPLIADA,
            Action.CONSULTAR_AUDITORIA,
            Action.CONFIGURAR_POLITICA_FRAUDE,
        }
    ),
    PrincipalRole.SUPERVISOR: frozenset(Action),
}


class AuthorizationDenied(PermissionError):
    """El principal no tiene permiso o alcance sobre la operación."""


def authorize(role: PrincipalRole, action: Action, *, resource_in_scope: bool) -> None:
    if action not in ROLE_PERMISSIONS[role]:
        raise AuthorizationDenied("Accion no permitida para el rol")
    if not resource_in_scope and role is not PrincipalRole.SUPERVISOR:
        raise AuthorizationDenied("Recurso fuera del alcance autorizado")


class AlertDetailLevel(StrEnum):
    RESUMEN = "resumen"
    DETALLE = "detalle"


def alert_detail_level(role: PrincipalRole) -> AlertDetailLevel:
    if Action.CONSULTAR_INFORMACION_AMPLIADA in ROLE_PERMISSIONS[role]:
        return AlertDetailLevel.DETALLE
    if Action.CONSULTAR_ALERTA_RESUMEN in ROLE_PERMISSIONS[role]:
        return AlertDetailLevel.RESUMEN
    raise AuthorizationDenied("Accion no permitida para el rol")


@dataclass(frozen=True, slots=True)
class PaymentApproval:
    preparer_id: str
    authorizer_id: str
    authorizer_role: PrincipalRole


def validate_payment_approval(approval: PaymentApproval) -> None:
    if not approval.preparer_id.strip() or not approval.authorizer_id.strip():
        raise AuthorizationDenied("Preparador y autorizador son obligatorios")
    if approval.preparer_id == approval.authorizer_id:
        raise AuthorizationDenied("La misma persona no puede preparar y autorizar el pago")
    if approval.authorizer_role is not PrincipalRole.SUPERVISOR:
        raise AuthorizationDenied("Solo un supervisor puede autorizar pagos en el piloto")
