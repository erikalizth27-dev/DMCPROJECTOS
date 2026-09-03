\set ON_ERROR_STOP on

BEGIN;

ALTER TABLE siniestro_facil.relacion_casos
    ADD COLUMN IF NOT EXISTS valor_normalizado varchar(255),
    ADD COLUMN IF NOT EXISTS estado_revision varchar(25) NOT NULL
        DEFAULT 'pendiente_revision';

CREATE UNIQUE INDEX IF NOT EXISTS uq_relacion_casos_par_criterio
    ON siniestro_facil.relacion_casos
        (id_siniestro_a, id_siniestro_b, criterio_relacion);

CREATE TABLE IF NOT EXISTS
    siniestro_facil.solicitud_relacion_casos_idempotente (
        clave varchar(128) PRIMARY KEY,
        huella varchar(64) NOT NULL,
        id_siniestro bigint NOT NULL REFERENCES
            siniestro_facil.siniestro (id_siniestro) ON DELETE CASCADE,
        respuesta jsonb NOT NULL,
        creado_en timestamptz NOT NULL DEFAULT statement_timestamp(),
        CONSTRAINT chk_solicitud_relacion_casos_clave
            CHECK (char_length(clave) BETWEEN 16 AND 128),
        CONSTRAINT chk_solicitud_relacion_casos_huella
            CHECK (char_length(huella) = 64)
    );

GRANT SELECT, INSERT
ON TABLE siniestro_facil.solicitud_relacion_casos_idempotente
TO siniestro_app;

GRANT SELECT, INSERT
ON TABLE siniestro_facil.relacion_casos
TO siniestro_app;

UPDATE siniestro_facil.alembic_version
SET version_num = '20260903_03'
WHERE version_num = '20260903_02';

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM siniestro_facil.alembic_version
        WHERE version_num = '20260903_03'
    ) THEN
        RAISE EXCEPTION 'No se actualizó alembic_version';
    END IF;
END
$$;

COMMIT;

SELECT version_num FROM siniestro_facil.alembic_version;
SELECT to_regclass(
    'siniestro_facil.solicitud_relacion_casos_idempotente'
) AS tabla_idempotencia_relaciones;
