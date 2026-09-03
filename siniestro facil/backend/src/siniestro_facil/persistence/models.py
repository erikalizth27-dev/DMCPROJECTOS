from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, CheckConstraint, Date, DateTime, ForeignKey, JSON, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


SCHEMA = "siniestro_facil"


class Base(DeclarativeBase):
    pass


class Asegurado(Base):
    __tablename__ = "asegurado"
    __table_args__ = {"schema": SCHEMA}

    id_asegurado: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    numero_documento: Mapped[str] = mapped_column(String(50), nullable=False)
    tipo_documento: Mapped[str | None] = mapped_column(String(30))
    medio_contacto: Mapped[str] = mapped_column(String(120), nullable=False)
    nombre: Mapped[str | None] = mapped_column(String(200))


class Reportante(Base):
    __tablename__ = "reportante"
    __table_args__ = {"schema": SCHEMA}

    id_reportante: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_asegurado: Mapped[int | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.asegurado.id_asegurado")
    )
    es_titular: Mapped[bool] = mapped_column(Boolean, nullable=False)
    medio_contacto: Mapped[str] = mapped_column(String(120), nullable=False)
    relacion_asegurado: Mapped[str | None] = mapped_column(String(30))


class Poliza(Base):
    __tablename__ = "poliza"
    __table_args__ = {"schema": SCHEMA}

    id_poliza: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    numero_poliza: Mapped[str] = mapped_column(String(50), nullable=False)
    id_asegurado: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.asegurado.id_asegurado"), nullable=False
    )
    vigente_desde: Mapped[date] = mapped_column(Date, nullable=False)
    vigente_hasta: Mapped[date] = mapped_column(Date, nullable=False)
    tipo_seguro: Mapped[str] = mapped_column(String(30), nullable=False)


class Vehiculo(Base):
    __tablename__ = "vehiculo"
    __table_args__ = {"schema": SCHEMA}

    id_vehiculo: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    placa: Mapped[str] = mapped_column(String(15), nullable=False)
    id_poliza: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.poliza.id_poliza"), nullable=False
    )


class Cobertura(Base):
    __tablename__ = "cobertura"
    __table_args__ = {"schema": SCHEMA}

    id_cobertura: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_poliza: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.poliza.id_poliza"), nullable=False
    )
    deducible: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    estado_validacion: Mapped[str | None] = mapped_column(String(30))


class Siniestro(Base):
    __tablename__ = "siniestro"
    __table_args__ = {"schema": SCHEMA}

    id_siniestro: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_poliza: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.poliza.id_poliza"), nullable=False
    )
    id_vehiculo: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.vehiculo.id_vehiculo"), nullable=False
    )
    id_reportante: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.reportante.id_reportante"), nullable=False
    )
    fecha_evento: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ubicacion_evento: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo_evento: Mapped[str] = mapped_column(String(50), nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    danos_aparentes: Mapped[str | None] = mapped_column(Text)
    estado_actual: Mapped[str] = mapped_column(String(30), nullable=False)
    canal_origen: Mapped[str | None] = mapped_column(String(30))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)


class EventoLineaTiempo(Base):
    __tablename__ = "evento_linea_tiempo"
    __table_args__ = {"schema": SCHEMA}

    id_evento: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_siniestro: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.siniestro.id_siniestro"), nullable=False
    )
    id_usuario: Mapped[int | None] = mapped_column(BigInteger)
    tipo_evento: Mapped[str] = mapped_column(String(50), nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    detalle: Mapped[dict[str, object] | None] = mapped_column(JSON)


class SolicitudIdempotente(Base):
    __tablename__ = "solicitud_idempotente"
    __table_args__ = {"schema": SCHEMA}

    clave: Mapped[str] = mapped_column(String(128), primary_key=True)
    huella: Mapped[str] = mapped_column(String(64), nullable=False)
    id_siniestro: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.siniestro.id_siniestro", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    respuesta: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class UsuarioInterno(Base):
    __tablename__ = "usuario_interno"
    __table_args__ = {"schema": SCHEMA}

    id_usuario: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    rol: Mapped[str] = mapped_column(String(30), nullable=False)


class Proveedor(Base):
    __tablename__ = "proveedor"
    __table_args__ = {"schema": SCHEMA}

    id_proveedor: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    tipo_proveedor: Mapped[str] = mapped_column(String(30), nullable=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)


class AsignacionSiniestro(Base):
    __tablename__ = "asignacion_siniestro"
    __table_args__ = {"schema": SCHEMA}

    id_asignacion: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_siniestro: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.siniestro.id_siniestro"), nullable=False
    )
    id_usuario: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.usuario_interno.id_usuario"), nullable=False
    )
    motivo: Mapped[str] = mapped_column(Text, nullable=False)
    asignado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finalizado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class IdentidadActor(Base):
    __tablename__ = "identidad_actor"
    __table_args__ = (
        CheckConstraint(
            "num_nonnulls(id_asegurado, id_usuario, id_proveedor) = 1",
            name="chk_identidad_actor_un_destino",
        ),
        {"schema": SCHEMA},
    )

    subject: Mapped[str] = mapped_column(String(255), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(120), primary_key=True)
    actor_type: Mapped[str] = mapped_column(String(20), nullable=False)
    id_asegurado: Mapped[int | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.asegurado.id_asegurado")
    )
    id_usuario: Mapped[int | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.usuario_interno.id_usuario")
    )
    id_proveedor: Mapped[int | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.proveedor.id_proveedor")
    )


class Evidencia(Base):
    __tablename__ = "evidencia"
    __table_args__ = {"schema": SCHEMA}

    id_evidencia: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_siniestro: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.siniestro.id_siniestro", ondelete="CASCADE"),
        nullable=False,
    )
    tipo_evidencia: Mapped[str] = mapped_column(String(50), nullable=False)
    contenido_original_uri: Mapped[str] = mapped_column(Text, nullable=False)
    hash: Mapped[str] = mapped_column(String(128), nullable=False)
    metadatos: Mapped[dict[str, object] | None] = mapped_column(JSON)
    fecha_captura: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fecha_recepcion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    fuente: Mapped[str | None] = mapped_column(String(50))
    ubicacion_captura: Mapped[str | None] = mapped_column(String(255))
    dispositivo_captura: Mapped[str | None] = mapped_column(String(120))
    version_derivada_de: Mapped[int | None] = mapped_column(
        ForeignKey(
            f"{SCHEMA}.evidencia.id_evidencia",
            ondelete="RESTRICT",
        )
    )


class SolicitudEvidenciaIdempotente(Base):
    __tablename__ = "solicitud_evidencia_idempotente"
    __table_args__ = {"schema": SCHEMA}

    clave: Mapped[str] = mapped_column(String(128), primary_key=True)
    huella: Mapped[str] = mapped_column(String(64), nullable=False)
    id_evidencia: Mapped[int] = mapped_column(
        ForeignKey(
            f"{SCHEMA}.evidencia.id_evidencia",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
    )
    respuesta: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class Asistencia(Base):
    __tablename__ = "asistencia"
    __table_args__ = {"schema": SCHEMA}

    id_asistencia: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_siniestro: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.siniestro.id_siniestro", ondelete="CASCADE"),
        nullable=False,
    )
    id_proveedor: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.proveedor.id_proveedor"),
        nullable=False,
    )
    estado_solicitud: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    numero_intento: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tipo_asistencia: Mapped[str] = mapped_column(String(50), nullable=False)
    motivo: Mapped[str] = mapped_column(Text, nullable=False)
    referencia_externa: Mapped[str | None] = mapped_column(String(120))
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class SolicitudAsistenciaIdempotente(Base):
    __tablename__ = "solicitud_asistencia_idempotente"
    __table_args__ = {"schema": SCHEMA}

    clave: Mapped[str] = mapped_column(String(128), primary_key=True)
    huella: Mapped[str] = mapped_column(String(64), nullable=False)
    id_asistencia: Mapped[int] = mapped_column(
        ForeignKey(
            f"{SCHEMA}.asistencia.id_asistencia",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
    )
    respuesta: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class EventoOutbox(Base):
    __tablename__ = "evento_outbox"
    __table_args__ = (
        CheckConstraint(
            "estado IN ('pendiente', 'publicando', 'publicado', 'fallido')",
            name="chk_evento_outbox_estado",
        ),
        CheckConstraint(
            "intentos >= 0",
            name="chk_evento_outbox_intentos",
        ),
        {"schema": SCHEMA},
    )

    id_evento_outbox: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )
    event_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        unique=True,
    )
    aggregate_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    aggregate_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )
    payload: Mapped[dict[str, object]] = mapped_column(
        JSON,
        nullable=False,
    )
    estado: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pendiente",
    )
    intentos: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
    )
    ocurrido_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    disponible_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    publicado_en: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
    pubsub_message_id: Mapped[str | None] = mapped_column(
        String(255),
    )
    ultimo_error: Mapped[str | None] = mapped_column(Text)


class Inspeccion(Base):
    __tablename__ = "inspeccion"
    __table_args__ = {"schema": SCHEMA}

    id_inspeccion: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )
    id_siniestro: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.siniestro.id_siniestro", ondelete="CASCADE"),
        nullable=False,
    )
    fecha_programada: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class Presupuesto(Base):
    __tablename__ = "presupuesto"
    __table_args__ = {"schema": SCHEMA}

    id_presupuesto: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )
    id_siniestro: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.siniestro.id_siniestro", ondelete="CASCADE"),
        nullable=False,
    )
    id_inspeccion: Mapped[int | None] = mapped_column(
        ForeignKey(f"{SCHEMA}.inspeccion.id_inspeccion", ondelete="RESTRICT")
    )
    id_proveedor: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.proveedor.id_proveedor", ondelete="RESTRICT"),
        nullable=False,
    )
    diagnostico: Mapped[str | None] = mapped_column(Text)
    vigencia_desde: Mapped[date] = mapped_column(Date, nullable=False)
    vigencia_hasta: Mapped[date] = mapped_column(Date, nullable=False)
    estado: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="recibido",
    )


class Autorizacion(Base):
    __tablename__ = "autorizacion"
    __table_args__ = {"schema": SCHEMA}

    id_autorizacion: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )
    id_usuario_autoriza: Mapped[int] = mapped_column(
        ForeignKey(
            f"{SCHEMA}.usuario_interno.id_usuario",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    objeto_autorizado: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )


class CambioPresupuesto(Base):
    __tablename__ = "cambio_presupuesto"
    __table_args__ = {"schema": SCHEMA}

    id_cambio: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )
    id_presupuesto: Mapped[int] = mapped_column(
        ForeignKey(
            f"{SCHEMA}.presupuesto.id_presupuesto",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    tipo_cambio: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    id_autorizacion: Mapped[int] = mapped_column(
        ForeignKey(
            f"{SCHEMA}.autorizacion.id_autorizacion",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )


class SolicitudPresupuestoIdempotente(Base):
    __tablename__ = "solicitud_presupuesto_idempotente"
    __table_args__ = {"schema": SCHEMA}

    clave: Mapped[str] = mapped_column(String(128), primary_key=True)
    huella: Mapped[str] = mapped_column(String(64), nullable=False)
    id_presupuesto: Mapped[int] = mapped_column(
        ForeignKey(
            f"{SCHEMA}.presupuesto.id_presupuesto",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
    )
    respuesta: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class SolicitudDecisionPresupuestoIdempotente(Base):
    __tablename__ = "solicitud_decision_presupuesto_idempotente"
    __table_args__ = {"schema": SCHEMA}

    clave: Mapped[str] = mapped_column(String(128), primary_key=True)
    huella: Mapped[str] = mapped_column(String(64), nullable=False)
    id_cambio: Mapped[int] = mapped_column(
        ForeignKey(
            f"{SCHEMA}.cambio_presupuesto.id_cambio",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
    )
    respuesta: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

class PoliticaAlerta(Base):
    __tablename__ = "politica_alerta"
    __table_args__ = {"schema": SCHEMA}

    id_politica_alerta: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    version: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    regla_bloqueo: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    vigente_desde: Mapped[date] = mapped_column(Date, nullable=False)


class Alerta(Base):
    __tablename__ = "alerta"
    __table_args__ = {"schema": SCHEMA}

    id_alerta: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_siniestro: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.siniestro.id_siniestro", ondelete="CASCADE"),
        nullable=False,
    )
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    severidad: Mapped[str] = mapped_column(String(20), nullable=False)
    explicacion: Mapped[str] = mapped_column(Text, nullable=False)
    datos_origen: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    fecha: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    modelo_o_regla: Mapped[str] = mapped_column(String(100), nullable=False)
    id_politica_alerta: Mapped[int] = mapped_column(
        ForeignKey(
            f"{SCHEMA}.politica_alerta.id_politica_alerta",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    estado_revision: Mapped[str] = mapped_column(
        String(25),
        nullable=False,
        default="pendiente",
    )
    justificacion_revision: Mapped[str | None] = mapped_column(Text)
    version: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)


class SenalRiesgo(Base):
    __tablename__ = "senal_riesgo"
    __table_args__ = {"schema": SCHEMA}

    id_senal: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_siniestro: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.siniestro.id_siniestro", ondelete="CASCADE"),
        nullable=False,
    )
    tipo_senal: Mapped[str] = mapped_column(String(40), nullable=False)
    origen: Mapped[str] = mapped_column(String(20), nullable=False)


class RelacionCasos(Base):
    __tablename__ = "relacion_casos"
    __table_args__ = (
        CheckConstraint(
            "id_siniestro_a < id_siniestro_b",
            name="chk_relacion_orden",
        ),
        {"schema": SCHEMA},
    )

    id_relacion: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_siniestro_a: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.siniestro.id_siniestro", ondelete="CASCADE"),
        nullable=False,
    )
    id_siniestro_b: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.siniestro.id_siniestro", ondelete="CASCADE"),
        nullable=False,
    )
    criterio_relacion: Mapped[str] = mapped_column(String(30), nullable=False)
    valor_normalizado: Mapped[str | None] = mapped_column(String(255))
    estado_revision: Mapped[str] = mapped_column(
        String(25), nullable=False, default="pendiente_revision"
    )


class SolicitudEvaluacionFraudeIdempotente(Base):
    __tablename__ = "solicitud_evaluacion_fraude_idempotente"
    __table_args__ = (
        CheckConstraint(
            "char_length(clave) BETWEEN 16 AND 128",
            name="chk_solicitud_evaluacion_fraude_clave",
        ),
        CheckConstraint(
            "char_length(huella) = 64",
            name="chk_solicitud_evaluacion_fraude_huella",
        ),
        {"schema": SCHEMA},
    )

    clave: Mapped[str] = mapped_column(String(128), primary_key=True)
    huella: Mapped[str] = mapped_column(String(64), nullable=False)
    id_siniestro: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.siniestro.id_siniestro", ondelete="CASCADE"),
        nullable=False,
    )
    respuesta: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )



class SolicitudRevisionAlertaIdempotente(Base):
    __tablename__ = "solicitud_revision_alerta_idempotente"
    __table_args__ = (
        CheckConstraint(
            "char_length(clave) BETWEEN 16 AND 128",
            name="chk_solicitud_revision_alerta_clave",
        ),
        CheckConstraint(
            "char_length(huella) = 64",
            name="chk_solicitud_revision_alerta_huella",
        ),
        {"schema": SCHEMA},
    )

    clave: Mapped[str] = mapped_column(String(128), primary_key=True)
    huella: Mapped[str] = mapped_column(String(64), nullable=False)
    id_alerta: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.alerta.id_alerta", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    respuesta: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )



class SolicitudRelacionCasosIdempotente(Base):
    __tablename__ = "solicitud_relacion_casos_idempotente"
    __table_args__ = (
        CheckConstraint(
            "char_length(clave) BETWEEN 16 AND 128",
            name="chk_solicitud_relacion_casos_clave",
        ),
        CheckConstraint(
            "char_length(huella) = 64",
            name="chk_solicitud_relacion_casos_huella",
        ),
        {"schema": SCHEMA},
    )

    clave: Mapped[str] = mapped_column(String(128), primary_key=True)
    huella: Mapped[str] = mapped_column(String(64), nullable=False)
    id_siniestro: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.siniestro.id_siniestro", ondelete="CASCADE"),
        nullable=False,
    )
    respuesta: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

class Pago(Base):
    __tablename__ = "pago"
    __table_args__ = (
        CheckConstraint("monto > 0", name="chk_pago_monto"),
        CheckConstraint(
            "estado IN ('bloqueado', 'emitido')",
            name="chk_pago_estado",
        ),
        CheckConstraint(
            "estado <> 'emitido' OR id_autorizacion IS NOT NULL",
            name="chk_pago_emitido_autorizado",
        ),
        {"schema": SCHEMA},
    )

    id_pago: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    id_siniestro: Mapped[int] = mapped_column(
        ForeignKey(
            f"{SCHEMA}.siniestro.id_siniestro",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    id_autorizacion: Mapped[int | None] = mapped_column(
        ForeignKey(
            f"{SCHEMA}.autorizacion.id_autorizacion",
            ondelete="RESTRICT",
        )
    )
    id_usuario_prepara: Mapped[int] = mapped_column(
        ForeignKey(
            f"{SCHEMA}.usuario_interno.id_usuario",
            ondelete="RESTRICT",
        ),
        nullable=False,
    )
    monto: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False)
    version: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
    )


class SolicitudPreparacionPagoIdempotente(Base):
    __tablename__ = "solicitud_preparacion_pago_idempotente"
    __table_args__ = {"schema": SCHEMA}

    clave: Mapped[str] = mapped_column(String(128), primary_key=True)
    huella: Mapped[str] = mapped_column(String(64), nullable=False)
    id_pago: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.pago.id_pago", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    respuesta: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class SolicitudAutorizacionPagoIdempotente(Base):
    __tablename__ = "solicitud_autorizacion_pago_idempotente"
    __table_args__ = {"schema": SCHEMA}

    clave: Mapped[str] = mapped_column(String(128), primary_key=True)
    huella: Mapped[str] = mapped_column(String(64), nullable=False)
    id_pago: Mapped[int] = mapped_column(
        ForeignKey(f"{SCHEMA}.pago.id_pago", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    respuesta: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )


class Comunicacion(Base):
    __tablename__ = "comunicacion"
    __table_args__ = {"schema": SCHEMA}

    id_comunicacion: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )
    id_siniestro: Mapped[int] = mapped_column(
        ForeignKey(
            f"{SCHEMA}.siniestro.id_siniestro",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    fecha: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    contenido: Mapped[str] = mapped_column(Text, nullable=False)

