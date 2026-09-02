\set ON_ERROR_STOP on

BEGIN;

CREATE TABLE IF NOT EXISTS
    siniestro_facil.solicitud_decision_presupuesto_idempotente (
        clave varchar(128) PRIMARY KEY,
        huella varchar(64) NOT NULL,
        id_cambio bigint NOT NULL UNIQUE
            REFERENCES siniestro_facil.cambio_presupuesto (id_cambio)
            ON DELETE CASCADE,
        respuesta jsonb NOT NULL,
        creado_en timestamptz NOT NULL DEFAULT statement_timestamp(),
        CONSTRAINT chk_solicitud_decision_presupuesto_clave
            CHECK (char_length(clave) BETWEEN 16 AND 128),
        CONSTRAINT chk_solicitud_decision_presupuesto_huella
            CHECK (char_length(huella) = 64)
    );

GRANT SELECT, INSERT
ON TABLE siniestro_facil.solicitud_decision_presupuesto_idempotente
TO siniestro_app;

UPDATE siniestro_facil.alembic_version
SET version_num = '20260902_04'
WHERE version_num = '20260902_03';

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM siniestro_facil.alembic_version
        WHERE version_num = '20260902_04'
    ) THEN
        RAISE EXCEPTION 'No se actualizó alembic_version';
    END IF;
END
$$;

COMMIT;

SELECT version_num FROM siniestro_facil.alembic_version;
SELECT to_regclass(
    'siniestro_facil.solicitud_decision_presupuesto_idempotente'
) AS tabla_idempotencia_decision;
