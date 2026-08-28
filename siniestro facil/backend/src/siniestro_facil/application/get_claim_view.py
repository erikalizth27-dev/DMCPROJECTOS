from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from siniestro_facil.domain.identity import AuthenticatedPrincipal


@dataclass(frozen=True, slots=True)
class ClaimView:
    id: int
    estado_actual: str
    fecha_evento: datetime
    tipo_evento: str
    siguiente_paso: str | None


class ClaimViewRepository(Protocol):
    def find_visible(
        self,
        claim_id: int,
        principal: AuthenticatedPrincipal,
    ) -> ClaimView | None: ...


class ClaimNotVisible(LookupError):
    """No diferencia entre inexistencia y falta de alcance."""


NEXT_STEP_BY_STATE = {
    "reportado": "validar_cobertura",
    "validando_cobertura": "completar_validacion",
    "asistencia_coordinada": "aportar_evidencia",
    "evidencia_pendiente": "completar_evidencia",
    "en_evaluacion": "programar_inspeccion",
    "inspeccion_programada": "recibir_presupuesto",
    "presupuesto_recibido": "revisar_presupuesto",
    "autorizado": "iniciar_reparacion_o_indemnizacion",
    "en_reparacion": "confirmar_reparacion",
    "listo_para_entrega": "confirmar_entrega",
    "indemnizado": "cerrar_siniestro",
    "observado": "resolver_observacion",
    "rechazado": "revisar_rechazo",
    "cerrado": None,
}


class GetClaimViewService:
    def __init__(self, repository: ClaimViewRepository) -> None:
        self._repository = repository

    def execute(
        self,
        claim_id: int,
        principal: AuthenticatedPrincipal,
    ) -> ClaimView:
        result = self._repository.find_visible(claim_id, principal)
        if result is None:
            raise ClaimNotVisible("Siniestro no encontrado")
        return result
