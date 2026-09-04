\set ON_ERROR_STOP on

BEGIN;

ALTER TABLE siniestro_facil.pago
    ADD COLUMN IF NOT EXISTS id_usuario_prepara bigint REFERENCES
        siniestro_facil.usuario_interno (id_usuario) ON DELETE RESTRICT,
    ADD COLUMN IF NOT EXISTS version bigint NOT NULL DEFAULT 0;

CREATE TABLE IF NOT EXISTS
    siniestro_facil.solicitud_preparacion_pago_idempotente (
        clave varchar(128) PRIMARY KEY,
        huella varchar(64) NOT NULL,
        id_pago bigint NOT NULL UNIQUE REFERENCES
            siniestro_facil.pago (id_pago) ON DELETE CASCADE,
        respuesta jsonb NOT NULL,
        creado_en timestamptz NOT NULL DEFAULT statement_timestamp(),
        CONSTRAINT chk_solicitud_preparacion_pago_clave
            CHECK (char_length(clave) BETWEEN 16 AND 128),
        CONSTRAINT chk_solicitud_preparacion_pago_huella
            CHECK (char_length(huella) = 64)
    );

CREATE TABLE IF NOT EXISTS
    siniestro_facil.solicitud_autorizacion_pago_idempotente (
        clave varchar(128) PRIMARY KEY,
        huella varchar(64) NOT NULL,
        id_pago bigint NOT NULL UNIQUE REFERENCES
            siniestro_facil.pago (id_pago) ON DELETE CASCADE,
        respuesta jsonb NOT NULL,
        creado_en timestamptz NOT NULL DEFAULT statement_timestamp(),
        CONSTRAINT chk_solicitud_autorizacion_pago_clave
            CHECK (char_length(clave) BETWEEN 16 AND 128),
        CONSTRAINT chk_solicitud_autorizacion_pago_huella
            CHECK (char_length(huella) = 64)
    );

GRANT SELECT, INSERT
ON TABLE
    siniestro_facil.solicitud_preparacion_pago_idempotente,
    siniestro_facil.solicitud_autorizacion_pago_idempotente
TO siniestro_app;

UPDATE siniestro_facil.alembic_version
SET version_num = '20260903_04'
WHERE version_num = '20260903_03';

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM siniestro_facil.alembic_version
        WHERE version_num = '20260903_04'
    ) THEN
        RAISE EXCEPTION 'No se actualizó alembic_version';
    END IF;
END
$$;

COMMIT;

SELECT version_num FROM siniestro_facil.alembic_version;
SELECT
    to_regclass(
        'siniestro_facil.solicitud_preparacion_pago_idempotente'
    ) AS tabla_preparacion,
    to_regclass(
        'siniestro_facil.solicitud_autorizacion_pago_idempotente'
    ) AS tabla_autorizacion,
    EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'siniestro_facil'
          AND table_name = 'pago'
          AND column_name = 'id_usuario_prepara'
    ) AS preparador_persistente,
    EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'siniestro_facil'
          AND table_name = 'pago'
          AND column_name = 'version'
    ) AS version_persistente;
