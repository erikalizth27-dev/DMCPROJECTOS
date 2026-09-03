\set ON_ERROR_STOP on

BEGIN;

ALTER TABLE siniestro_facil.alerta
    ADD COLUMN IF NOT EXISTS version bigint NOT NULL DEFAULT 0;

CREATE TABLE IF NOT EXISTS
    siniestro_facil.solicitud_revision_alerta_idempotente (
        clave varchar(128) PRIMARY KEY,
        huella varchar(64) NOT NULL,
        id_alerta bigint NOT NULL UNIQUE REFERENCES
            siniestro_facil.alerta (id_alerta) ON DELETE CASCADE,
        respuesta jsonb NOT NULL,
        creado_en timestamptz NOT NULL DEFAULT statement_timestamp(),
        CONSTRAINT chk_solicitud_revision_alerta_clave
            CHECK (char_length(clave) BETWEEN 16 AND 128),
        CONSTRAINT chk_solicitud_revision_alerta_huella
            CHECK (char_length(huella) = 64)
    );

GRANT SELECT, INSERT
ON TABLE siniestro_facil.solicitud_revision_alerta_idempotente
TO siniestro_app;

GRANT SELECT, UPDATE
ON TABLE siniestro_facil.alerta
TO siniestro_app;

UPDATE siniestro_facil.alembic_version
SET version_num = '20260903_02'
WHERE version_num = '20260903_01';

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM siniestro_facil.alembic_version
        WHERE version_num = '20260903_02'
    ) THEN
        RAISE EXCEPTION 'No se actualizó alembic_version';
    END IF;
END
$$;

COMMIT;

SELECT version_num FROM siniestro_facil.alembic_version;
SELECT to_regclass(
    'siniestro_facil.solicitud_revision_alerta_idempotente'
) AS tabla_idempotencia_revision;
