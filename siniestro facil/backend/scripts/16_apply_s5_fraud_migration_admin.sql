\set ON_ERROR_STOP on

BEGIN;

CREATE TABLE IF NOT EXISTS
    siniestro_facil.solicitud_evaluacion_fraude_idempotente (
        clave varchar(128) PRIMARY KEY,
        huella varchar(64) NOT NULL,
        id_siniestro bigint NOT NULL REFERENCES
            siniestro_facil.siniestro (id_siniestro) ON DELETE CASCADE,
        respuesta jsonb NOT NULL,
        creado_en timestamptz NOT NULL DEFAULT statement_timestamp(),
        CONSTRAINT chk_solicitud_evaluacion_fraude_clave
            CHECK (char_length(clave) BETWEEN 16 AND 128),
        CONSTRAINT chk_solicitud_evaluacion_fraude_huella
            CHECK (char_length(huella) = 64)
    );

CREATE INDEX IF NOT EXISTS idx_solicitud_evaluacion_fraude_siniestro
    ON siniestro_facil.solicitud_evaluacion_fraude_idempotente
        (id_siniestro, creado_en);

GRANT SELECT, INSERT
ON TABLE siniestro_facil.solicitud_evaluacion_fraude_idempotente
TO siniestro_app;

UPDATE siniestro_facil.alembic_version
SET version_num = '20260903_01'
WHERE version_num = '20260902_05';

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM siniestro_facil.alembic_version
        WHERE version_num = '20260903_01'
    ) THEN
        RAISE EXCEPTION 'No se actualizó alembic_version';
    END IF;
END
$$;

COMMIT;

SELECT version_num FROM siniestro_facil.alembic_version;
SELECT to_regclass(
    'siniestro_facil.solicitud_evaluacion_fraude_idempotente'
) AS tabla_idempotencia;
