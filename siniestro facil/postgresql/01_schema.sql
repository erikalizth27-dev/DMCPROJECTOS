BEGIN;

CREATE SCHEMA IF NOT EXISTS siniestro_facil;
SET search_path TO siniestro_facil, public;

CREATE TABLE asegurado (
    id_asegurado bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    numero_documento varchar(50) NOT NULL,
    tipo_documento varchar(30),
    medio_contacto varchar(120) NOT NULL,
    nombre varchar(200),
    CONSTRAINT uq_asegurado_documento UNIQUE (tipo_documento, numero_documento),
    CONSTRAINT chk_asegurado_documento_no_vacio CHECK (btrim(numero_documento) <> ''),
    CONSTRAINT chk_asegurado_contacto_no_vacio CHECK (btrim(medio_contacto) <> '')
);

CREATE TABLE reportante (
    id_reportante bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_asegurado bigint REFERENCES asegurado (id_asegurado) ON DELETE RESTRICT,
    es_titular boolean NOT NULL,
    medio_contacto varchar(120) NOT NULL,
    CONSTRAINT chk_reportante_titular CHECK (NOT es_titular OR id_asegurado IS NOT NULL),
    CONSTRAINT chk_reportante_contacto_no_vacio CHECK (btrim(medio_contacto) <> '')
);

CREATE TABLE poliza (
    id_poliza bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    numero_poliza varchar(50) NOT NULL,
    id_asegurado bigint NOT NULL REFERENCES asegurado (id_asegurado) ON DELETE RESTRICT,
    vigente_desde date NOT NULL,
    vigente_hasta date NOT NULL,
    tipo_seguro varchar(30) NOT NULL DEFAULT 'vehicular',
    CONSTRAINT uq_poliza_numero UNIQUE (numero_poliza),
    CONSTRAINT chk_poliza_vigencia CHECK (vigente_hasta >= vigente_desde),
    CONSTRAINT chk_poliza_tipo CHECK (tipo_seguro = 'vehicular')
);

CREATE TABLE vehiculo (
    id_vehiculo bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    placa varchar(15) NOT NULL,
    id_poliza bigint NOT NULL REFERENCES poliza (id_poliza) ON DELETE RESTRICT,
    CONSTRAINT uq_vehiculo_placa_poliza UNIQUE (placa, id_poliza),
    CONSTRAINT uq_vehiculo_id_poliza UNIQUE (id_vehiculo, id_poliza),
    CONSTRAINT chk_vehiculo_placa_no_vacia CHECK (btrim(placa) <> '')
);

CREATE TABLE cobertura (
    id_cobertura bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_poliza bigint NOT NULL REFERENCES poliza (id_poliza) ON DELETE CASCADE,
    deducible numeric(12,2),
    estado_validacion varchar(30),
    CONSTRAINT chk_cobertura_deducible CHECK (deducible IS NULL OR deducible >= 0)
);

CREATE TABLE siniestro (
    id_siniestro bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_poliza bigint NOT NULL REFERENCES poliza (id_poliza) ON DELETE RESTRICT,
    id_vehiculo bigint NOT NULL,
    id_reportante bigint NOT NULL REFERENCES reportante (id_reportante) ON DELETE RESTRICT,
    fecha_evento timestamptz NOT NULL,
    ubicacion_evento varchar(255) NOT NULL,
    tipo_evento varchar(50) NOT NULL,
    descripcion text,
    danos_aparentes text,
    estado_actual varchar(30) NOT NULL DEFAULT 'reportado',
    canal_origen varchar(30),
    creado_en timestamptz NOT NULL DEFAULT statement_timestamp(),
    CONSTRAINT fk_siniestro_vehiculo_poliza FOREIGN KEY (id_vehiculo, id_poliza)
        REFERENCES vehiculo (id_vehiculo, id_poliza) ON DELETE RESTRICT,
    CONSTRAINT chk_siniestro_estado CHECK (estado_actual IN (
        'reportado','validando_cobertura','asistencia_coordinada','evidencia_pendiente',
        'en_evaluacion','inspeccion_programada','presupuesto_recibido','autorizado',
        'observado','rechazado','en_reparacion','listo_para_entrega','indemnizado','cerrado'
    )),
    CONSTRAINT chk_siniestro_ubicacion_no_vacia CHECK (btrim(ubicacion_evento) <> ''),
    CONSTRAINT chk_siniestro_tipo_no_vacio CHECK (btrim(tipo_evento) <> ''),
    CONSTRAINT chk_siniestro_fecha CHECK (fecha_evento <= creado_en)
);

CREATE TABLE participante (
    id_participante bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_siniestro bigint NOT NULL REFERENCES siniestro (id_siniestro) ON DELETE CASCADE,
    rol varchar(30) NOT NULL,
    nombre_declarado varchar(200),
    nombre_normalizado varchar(200),
    CONSTRAINT chk_participante_rol_no_vacio CHECK (btrim(rol) <> '')
);

CREATE TABLE evidencia (
    id_evidencia bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_siniestro bigint NOT NULL REFERENCES siniestro (id_siniestro) ON DELETE CASCADE,
    tipo_evidencia varchar(50) NOT NULL,
    contenido_original_uri text NOT NULL,
    hash varchar(128) NOT NULL,
    metadatos jsonb,
    fecha_captura timestamptz,
    fecha_recepcion timestamptz NOT NULL DEFAULT statement_timestamp(),
    fuente varchar(50),
    ubicacion_captura varchar(255),
    dispositivo_captura varchar(120),
    version_derivada_de bigint REFERENCES evidencia (id_evidencia) ON DELETE RESTRICT,
    CONSTRAINT uq_evidencia_hash_uri UNIQUE (hash, contenido_original_uri),
    CONSTRAINT chk_evidencia_hash_no_vacio CHECK (btrim(hash) <> ''),
    CONSTRAINT chk_evidencia_uri_no_vacia CHECK (btrim(contenido_original_uri) <> ''),
    CONSTRAINT chk_evidencia_version CHECK (version_derivada_de IS NULL OR version_derivada_de <> id_evidencia),
    CONSTRAINT chk_evidencia_fechas CHECK (fecha_captura IS NULL OR fecha_recepcion >= fecha_captura)
);

CREATE OR REPLACE FUNCTION impedir_mutacion_evidencia_original()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.id_siniestro IS DISTINCT FROM OLD.id_siniestro
       OR NEW.contenido_original_uri IS DISTINCT FROM OLD.contenido_original_uri
       OR NEW.hash IS DISTINCT FROM OLD.hash
       OR NEW.fecha_recepcion IS DISTINCT FROM OLD.fecha_recepcion
       OR NEW.fuente IS DISTINCT FROM OLD.fuente THEN
        RAISE EXCEPTION USING ERRCODE = 'integrity_constraint_violation',
            MESSAGE = 'Los datos originales de la evidencia son inmutables';
    END IF;
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_evidencia_original_inmutable
BEFORE UPDATE ON evidencia FOR EACH ROW
EXECUTE FUNCTION impedir_mutacion_evidencia_original();

CREATE TABLE proveedor (
    id_proveedor bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tipo_proveedor varchar(30) NOT NULL,
    nombre varchar(200),
    CONSTRAINT chk_proveedor_tipo CHECK (tipo_proveedor IN ('taller','grua'))
);

CREATE TABLE asistencia (
    id_asistencia bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_siniestro bigint NOT NULL REFERENCES siniestro (id_siniestro) ON DELETE CASCADE,
    id_proveedor bigint REFERENCES proveedor (id_proveedor) ON DELETE RESTRICT,
    estado_solicitud varchar(20) NOT NULL,
    numero_intento integer NOT NULL DEFAULT 1,
    CONSTRAINT chk_asistencia_estado CHECK (estado_solicitud IN ('aceptada','rechazada','sin_respuesta')),
    CONSTRAINT chk_asistencia_intento CHECK (numero_intento > 0),
    CONSTRAINT uq_asistencia_intento UNIQUE (id_siniestro, id_proveedor, numero_intento)
);

CREATE TABLE inspeccion (
    id_inspeccion bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_siniestro bigint NOT NULL REFERENCES siniestro (id_siniestro) ON DELETE CASCADE,
    fecha_programada timestamptz NOT NULL
);

CREATE TABLE presupuesto (
    id_presupuesto bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_siniestro bigint NOT NULL REFERENCES siniestro (id_siniestro) ON DELETE CASCADE,
    id_proveedor bigint NOT NULL REFERENCES proveedor (id_proveedor) ON DELETE RESTRICT,
    diagnostico text,
    vigencia_desde date NOT NULL,
    vigencia_hasta date NOT NULL,
    estado varchar(20) NOT NULL DEFAULT 'recibido',
    CONSTRAINT chk_presupuesto_vigencia CHECK (vigencia_hasta >= vigencia_desde),
    CONSTRAINT chk_presupuesto_estado CHECK (estado IN ('recibido','observado','autorizado','rechazado'))
);

CREATE TABLE usuario_interno (
    id_usuario bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    rol varchar(30) NOT NULL,
    CONSTRAINT chk_usuario_rol CHECK (rol IN ('operador','ajustador','investigador_fraude','supervisor'))
);

CREATE TABLE autorizacion (
    id_autorizacion bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_usuario_autoriza bigint NOT NULL REFERENCES usuario_interno (id_usuario) ON DELETE RESTRICT,
    fecha timestamptz NOT NULL DEFAULT statement_timestamp(),
    objeto_autorizado varchar(50) NOT NULL,
    CONSTRAINT chk_autorizacion_objeto_no_vacio CHECK (btrim(objeto_autorizado) <> '')
);

CREATE TABLE cambio_presupuesto (
    id_cambio bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_presupuesto bigint NOT NULL REFERENCES presupuesto (id_presupuesto) ON DELETE CASCADE,
    tipo_cambio varchar(30) NOT NULL,
    id_autorizacion bigint NOT NULL REFERENCES autorizacion (id_autorizacion) ON DELETE RESTRICT,
    CONSTRAINT chk_cambio_tipo CHECK (tipo_cambio IN ('observacion','repuesto_alternativo','ampliacion'))
);

CREATE TABLE politica_alerta (
    id_politica_alerta bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    version varchar(20) NOT NULL,
    regla_bloqueo jsonb NOT NULL,
    vigente_desde date NOT NULL,
    CONSTRAINT uq_politica_version UNIQUE (version),
    CONSTRAINT chk_politica_regla_objeto CHECK (jsonb_typeof(regla_bloqueo) = 'object')
);

CREATE TABLE alerta (
    id_alerta bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_siniestro bigint NOT NULL REFERENCES siniestro (id_siniestro) ON DELETE CASCADE,
    tipo varchar(50) NOT NULL,
    severidad varchar(20) NOT NULL,
    explicacion text NOT NULL,
    datos_origen jsonb NOT NULL,
    fecha timestamptz NOT NULL DEFAULT statement_timestamp(),
    modelo_o_regla varchar(100) NOT NULL,
    id_politica_alerta bigint NOT NULL REFERENCES politica_alerta (id_politica_alerta) ON DELETE RESTRICT,
    estado_revision varchar(25) NOT NULL DEFAULT 'pendiente',
    justificacion_revision text,
    CONSTRAINT chk_alerta_estado CHECK (estado_revision IN ('pendiente','confirmada','descartada','en_solicitud_info')),
    CONSTRAINT chk_alerta_revision CHECK (
        estado_revision IN ('pendiente','en_solicitud_info') OR btrim(coalesce(justificacion_revision,'')) <> ''
    )
);

CREATE TABLE senal_riesgo (
    id_senal bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_siniestro bigint NOT NULL REFERENCES siniestro (id_siniestro) ON DELETE CASCADE,
    tipo_senal varchar(40) NOT NULL,
    origen varchar(20) NOT NULL,
    CONSTRAINT chk_senal_tipo CHECK (tipo_senal IN (
        'participante_repetido','poliza_reciente','ubicacion_incoherente','foto_reutilizada',
        'monto_atipico','version_contradictoria','patron_contacto_compartido','antecedente_reclamo'
    )),
    CONSTRAINT chk_senal_origen CHECK (origen IN ('deterministica','modelo'))
);

CREATE TABLE relacion_casos (
    id_relacion bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_siniestro_a bigint NOT NULL REFERENCES siniestro (id_siniestro) ON DELETE CASCADE,
    id_siniestro_b bigint NOT NULL REFERENCES siniestro (id_siniestro) ON DELETE CASCADE,
    criterio_relacion varchar(30) NOT NULL,
    CONSTRAINT chk_relacion_orden CHECK (id_siniestro_a < id_siniestro_b),
    CONSTRAINT chk_relacion_criterio CHECK (criterio_relacion IN ('accidente','telefono','cuenta_bancaria','taller','persona')),
    CONSTRAINT uq_relacion_casos UNIQUE (id_siniestro_a, id_siniestro_b, criterio_relacion)
);

CREATE TABLE pago (
    id_pago bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_siniestro bigint NOT NULL REFERENCES siniestro (id_siniestro) ON DELETE RESTRICT,
    id_autorizacion bigint REFERENCES autorizacion (id_autorizacion) ON DELETE RESTRICT,
    monto numeric(14,2) NOT NULL,
    estado varchar(20) NOT NULL,
    CONSTRAINT chk_pago_monto CHECK (monto > 0),
    CONSTRAINT chk_pago_estado CHECK (estado IN ('bloqueado','emitido')),
    CONSTRAINT chk_pago_emitido_autorizado CHECK (estado <> 'emitido' OR id_autorizacion IS NOT NULL)
);

CREATE TABLE comunicacion (
    id_comunicacion bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_siniestro bigint NOT NULL REFERENCES siniestro (id_siniestro) ON DELETE CASCADE,
    fecha timestamptz NOT NULL DEFAULT statement_timestamp(),
    contenido text NOT NULL,
    CONSTRAINT chk_comunicacion_contenido CHECK (btrim(contenido) <> '')
);

CREATE TABLE evento_linea_tiempo (
    id_evento bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_siniestro bigint NOT NULL REFERENCES siniestro (id_siniestro) ON DELETE CASCADE,
    id_usuario bigint REFERENCES usuario_interno (id_usuario) ON DELETE RESTRICT,
    tipo_evento varchar(50) NOT NULL,
    fecha timestamptz NOT NULL DEFAULT statement_timestamp(),
    detalle jsonb,
    CONSTRAINT chk_evento_tipo_no_vacio CHECK (btrim(tipo_evento) <> '')
);

CREATE INDEX idx_poliza_asegurado ON poliza (id_asegurado);
CREATE INDEX idx_vehiculo_poliza ON vehiculo (id_poliza);
CREATE INDEX idx_siniestro_poliza ON siniestro (id_poliza);
CREATE INDEX idx_siniestro_estado ON siniestro (estado_actual);
CREATE INDEX idx_evidencia_siniestro ON evidencia (id_siniestro);
CREATE INDEX idx_evidencia_hash ON evidencia (hash);
CREATE INDEX idx_alerta_siniestro_estado ON alerta (id_siniestro, estado_revision);
CREATE INDEX idx_senal_siniestro ON senal_riesgo (id_siniestro);
CREATE INDEX idx_relacion_casos_b ON relacion_casos (id_siniestro_b);
CREATE INDEX idx_evento_siniestro_fecha ON evento_linea_tiempo (id_siniestro, fecha);

COMMIT;
