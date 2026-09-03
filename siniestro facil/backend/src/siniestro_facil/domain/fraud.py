from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import unicodedata


class RiskSignalType(StrEnum):
    PARTICIPANTE_REPETIDO = "participante_repetido"
    POLIZA_RECIENTE = "poliza_reciente"
    UBICACION_INCOHERENTE = "ubicacion_incoherente"
    FOTO_REUTILIZADA = "foto_reutilizada"
    MONTO_ATIPICO = "monto_atipico"
    VERSION_CONTRADICTORIA = "version_contradictoria"
    PATRON_CONTACTO_COMPARTIDO = "patron_contacto_compartido"
    ANTECEDENTE_RECLAMO = "antecedente_reclamo"


class SignalOrigin(StrEnum):
    DETERMINISTICA = "deterministica"
    MODELO = "modelo"


class AlertSeverity(StrEnum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class AlertReviewStatus(StrEnum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    DESCARTADA = "descartada"
    EN_SOLICITUD_INFO = "en_solicitud_info"


class AlertEffect(StrEnum):
    PRIORIZAR = "priorizar"
    DERIVAR_INVESTIGACION = "derivar_investigacion"
    BLOQUEAR_PAGO_HASTA_REVISION = "bloquear_pago_hasta_revision"


class RelationCriterion(StrEnum):
    ACCIDENTE = "accidente"
    TELEFONO = "telefono"
    CUENTA_BANCARIA = "cuenta_bancaria"
    TALLER = "taller"
    PERSONA = "persona"


def effect_for_severity(severity: AlertSeverity) -> AlertEffect:
    if severity is AlertSeverity.CRITICA:
        return AlertEffect.BLOQUEAR_PAGO_HASTA_REVISION
    if severity is AlertSeverity.ALTA:
        return AlertEffect.DERIVAR_INVESTIGACION
    return AlertEffect.PRIORIZAR


def normalize_exact_value(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value)
    return " ".join(normalized.strip().upper().split())


def canonical_claim_pair(claim_a: int, claim_b: int) -> tuple[int, int]:
    if claim_a <= 0 or claim_b <= 0:
        raise ValueError("Los identificadores de siniestro deben ser positivos")
    if claim_a == claim_b:
        raise ValueError("Un siniestro no puede relacionarse consigo mismo")
    return min(claim_a, claim_b), max(claim_a, claim_b)


@dataclass(frozen=True, slots=True)
class RiskSignal:
    signal_type: RiskSignalType
    origin: SignalOrigin
    source_data: dict[str, object]


@dataclass(frozen=True, slots=True)
class AlertRecommendation:
    alert_type: str
    severity: AlertSeverity
    explanation: str
    source_data: dict[str, object]
    rule_or_model: str
    policy_version: str

    @property
    def effect(self) -> AlertEffect:
        return effect_for_severity(self.severity)
