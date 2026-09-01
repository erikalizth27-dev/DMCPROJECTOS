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
