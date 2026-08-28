from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from siniestro_facil.domain.enums import EstadoSiniestro


class ApiModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class CrearSiniestroRequest(ApiModel):
    numero_poliza: str | None = Field(default=None, alias="numeroPoliza", min_length=1)
    numero_documento: str | None = Field(default=None, alias="numeroDocumento", min_length=1)
    placa: str = Field(min_length=1, max_length=15)
    fecha_evento: datetime = Field(alias="fechaEvento")
    ubicacion_evento: str = Field(alias="ubicacionEvento", min_length=1, max_length=255)
    tipo_evento: str = Field(alias="tipoEvento", min_length=1, max_length=50)
    medio_contacto: str = Field(alias="medioContacto", min_length=1, max_length=120)

    @model_validator(mode="after")
    def require_policy_or_document(self) -> "CrearSiniestroRequest":
        if not self.numero_poliza and not self.numero_documento:
            raise ValueError("Debe informar numeroPoliza o numeroDocumento")
        return self


class SiniestroResponse(ApiModel):
    id: int
    estado_actual: EstadoSiniestro = Field(alias="estadoActual")
    fecha_evento: datetime = Field(alias="fechaEvento")
    tipo_evento: str = Field(alias="tipoEvento")
    siguiente_paso: str | None = Field(default=None, alias="siguientePaso")


class CambiarEstadoRequest(ApiModel):
    estado_destino: EstadoSiniestro = Field(alias="estadoDestino")
    motivo: str = Field(min_length=1, max_length=500)
    version: int = Field(ge=0)


class CambiarEstadoResponse(ApiModel):
    id: int
    estado_actual: EstadoSiniestro = Field(alias="estadoActual")
    version: int = Field(ge=1)


class RegistrarEvidenciaRequest(ApiModel):
    tipo_evidencia: str = Field(alias="tipoEvidencia", min_length=1, max_length=50)
    contenido_original_uri: HttpUrl = Field(alias="contenidoOriginalUri")
    hash: str = Field(min_length=1, max_length=128)
    fecha_captura: datetime | None = Field(default=None, alias="fechaCaptura")
    fuente: str | None = Field(default=None, max_length=50)
    version_derivada_de: int | None = Field(default=None, alias="versionDerivadaDe", gt=0)


class SolicitarAsistenciaRequest(ApiModel):
    tipo_proveedor: str = Field(alias="tipoProveedor", min_length=1, max_length=30)
    ubicacion: str = Field(min_length=1, max_length=255)


class RegistrarPresupuestoRequest(ApiModel):
    proveedor_id: int = Field(alias="proveedorId", gt=0)
    diagnostico: str | None = None
    vigencia_desde: date = Field(alias="vigenciaDesde")
    vigencia_hasta: date = Field(alias="vigenciaHasta")

    @model_validator(mode="after")
    def validate_dates(self) -> "RegistrarPresupuestoRequest":
        if self.vigencia_hasta < self.vigencia_desde:
            raise ValueError("vigenciaHasta no puede ser anterior a vigenciaDesde")
        return self


class EstadoRevisionAlerta(StrEnum):
    CONFIRMADA = "confirmada"
    DESCARTADA = "descartada"
    EN_SOLICITUD_INFO = "en_solicitud_info"


class RevisarAlertaRequest(ApiModel):
    estado_revision: EstadoRevisionAlerta = Field(alias="estadoRevision")
    justificacion: str = Field(min_length=1, max_length=2000)


class AlertaResumenResponse(ApiModel):
    id: int = Field(gt=0)
    severidad: str = Field(min_length=1)
    estado_revision: str = Field(alias="estadoRevision", min_length=1)


class AlertaDetalleResponse(AlertaResumenResponse):
    tipo: str = Field(min_length=1)
    detalle: dict[str, object] = Field(default_factory=dict)


class PrepararSolicitudPagoRequest(ApiModel):
    monto: Decimal = Field(gt=0, max_digits=14, decimal_places=2)


class AutorizarSolicitudPagoRequest(ApiModel):
    confirmacion_humana: Literal[True] = Field(alias="confirmacionHumana")


class ErrorResponse(ApiModel):
    codigo: str
    mensaje: str
    correlation_id: str = Field(alias="correlationId")
    detalles: list[str] = Field(default_factory=list)
