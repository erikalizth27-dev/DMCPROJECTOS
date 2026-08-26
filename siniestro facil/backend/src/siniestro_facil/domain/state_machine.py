from __future__ import annotations

from dataclasses import dataclass

from .enums import EstadoSiniestro, RolUsuario


class TransicionNoPermitida(ValueError):
    """La transición solicitada contradice las reglas del flujo."""


TRANSICIONES: dict[EstadoSiniestro, frozenset[EstadoSiniestro]] = {
    EstadoSiniestro.REPORTADO: frozenset(
        {EstadoSiniestro.VALIDANDO_COBERTURA, EstadoSiniestro.RECHAZADO}
    ),
    EstadoSiniestro.VALIDANDO_COBERTURA: frozenset(
        {
            EstadoSiniestro.ASISTENCIA_COORDINADA,
            EstadoSiniestro.EVIDENCIA_PENDIENTE,
            EstadoSiniestro.EN_EVALUACION,
            EstadoSiniestro.RECHAZADO,
        }
    ),
    EstadoSiniestro.ASISTENCIA_COORDINADA: frozenset(
        {EstadoSiniestro.EVIDENCIA_PENDIENTE, EstadoSiniestro.EN_EVALUACION}
    ),
    EstadoSiniestro.EVIDENCIA_PENDIENTE: frozenset({EstadoSiniestro.EN_EVALUACION}),
    EstadoSiniestro.EN_EVALUACION: frozenset(
        {
            EstadoSiniestro.INSPECCION_PROGRAMADA,
            EstadoSiniestro.PRESUPUESTO_RECIBIDO,
            EstadoSiniestro.OBSERVADO,
            EstadoSiniestro.RECHAZADO,
        }
    ),
    EstadoSiniestro.INSPECCION_PROGRAMADA: frozenset(
        {EstadoSiniestro.PRESUPUESTO_RECIBIDO, EstadoSiniestro.OBSERVADO}
    ),
    EstadoSiniestro.PRESUPUESTO_RECIBIDO: frozenset(
        {EstadoSiniestro.AUTORIZADO, EstadoSiniestro.OBSERVADO, EstadoSiniestro.RECHAZADO}
    ),
    EstadoSiniestro.AUTORIZADO: frozenset(
        {EstadoSiniestro.EN_REPARACION, EstadoSiniestro.INDEMNIZADO}
    ),
    EstadoSiniestro.EN_REPARACION: frozenset(
        {EstadoSiniestro.LISTO_PARA_ENTREGA, EstadoSiniestro.OBSERVADO}
    ),
    EstadoSiniestro.LISTO_PARA_ENTREGA: frozenset({EstadoSiniestro.CERRADO}),
    EstadoSiniestro.INDEMNIZADO: frozenset({EstadoSiniestro.CERRADO}),
    EstadoSiniestro.OBSERVADO: frozenset(
        {
            EstadoSiniestro.EVIDENCIA_PENDIENTE,
            EstadoSiniestro.EN_EVALUACION,
            EstadoSiniestro.PRESUPUESTO_RECIBIDO,
            EstadoSiniestro.RECHAZADO,
        }
    ),
    EstadoSiniestro.RECHAZADO: frozenset(
        {EstadoSiniestro.EN_EVALUACION, EstadoSiniestro.CERRADO}
    ),
    EstadoSiniestro.CERRADO: frozenset(),
}


@dataclass(frozen=True, slots=True)
class SolicitudTransicion:
    origen: EstadoSiniestro
    destino: EstadoSiniestro
    rol: RolUsuario
    motivo: str
    evidencia_completa: bool = False
    confirmacion_humana: bool = False


def validar_transicion(solicitud: SolicitudTransicion) -> None:
    if not solicitud.motivo.strip():
        raise TransicionNoPermitida("El motivo es obligatorio")
    if solicitud.destino not in TRANSICIONES[solicitud.origen]:
        raise TransicionNoPermitida(
            f"Transicion {solicitud.origen.value} -> {solicitud.destino.value} no permitida"
        )
    if (
        solicitud.origen is EstadoSiniestro.RECHAZADO
        and solicitud.destino is EstadoSiniestro.EN_EVALUACION
        and solicitud.rol is not RolUsuario.SUPERVISOR
    ):
        raise TransicionNoPermitida("Solo un supervisor puede reabrir un rechazo")
    if solicitud.destino is EstadoSiniestro.RECHAZADO and not solicitud.confirmacion_humana:
        raise TransicionNoPermitida("El rechazo requiere confirmacion humana")
    if (
        solicitud.origen is EstadoSiniestro.EVIDENCIA_PENDIENTE
        and solicitud.destino is EstadoSiniestro.EN_EVALUACION
        and not solicitud.evidencia_completa
    ):
        raise TransicionNoPermitida("El checklist de evidencia debe estar completo")

