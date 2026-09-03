\set ON_ERROR_STOP on

BEGIN;

ALTER TABLE siniestro_facil.cambio_presupuesto
    DROP CONSTRAINT IF EXISTS chk_cambio_tipo;

ALTER TABLE siniestro_facil.cambio_presupuesto
    ADD CONSTRAINT chk_cambio_tipo CHECK (
        tipo_cambio IN (
            'observacion',
            'repuesto_alternativo',
            'ampliacion',
            'aprobacion',
            'rechazo'
        )
    );

UPDATE siniestro_facil.alembic_version
SET version_num = '20260902_05'
WHERE version_num = '20260902_04';

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM siniestro_facil.alembic_version
        WHERE version_num = '20260902_05'
    ) THEN
        RAISE EXCEPTION 'No se actualizó alembic_version a 20260902_05';
    END IF;
END
$$;

COMMIT;

SELECT version_num
FROM siniestro_facil.alembic_version;

SELECT pg_get_constraintdef(oid) AS chk_cambio_tipo
FROM pg_constraint
WHERE conrelid = 'siniestro_facil.cambio_presupuesto'::regclass
  AND conname = 'chk_cambio_tipo';
