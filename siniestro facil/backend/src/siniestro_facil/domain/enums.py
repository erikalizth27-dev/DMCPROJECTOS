from enum import StrEnum


class EstadoSiniestro(StrEnum):
    REPORTADO = "reportado"
    VALIDANDO_COBERTURA = "validando_cobertura"
    ASISTENCIA_COORDINADA = "asistencia_coordinada"
    EVIDENCIA_PENDIENTE = "evidencia_pendiente"
    EN_EVALUACION = "en_evaluacion"
    INSPECCION_PROGRAMADA = "inspeccion_programada"
    PRESUPUESTO_RECIBIDO = "presupuesto_recibido"
    AUTORIZADO = "autorizado"
    OBSERVADO = "observado"
    RECHAZADO = "rechazado"
    EN_REPARACION = "en_reparacion"
    LISTO_PARA_ENTREGA = "listo_para_entrega"
    INDEMNIZADO = "indemnizado"
    CERRADO = "cerrado"


class RolUsuario(StrEnum):
    OPERADOR = "operador"
    AJUSTADOR = "ajustador"
    INVESTIGADOR_FRAUDE = "investigador_fraude"
    SUPERVISOR = "supervisor"

