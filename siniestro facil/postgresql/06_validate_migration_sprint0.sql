\set ON_ERROR_STOP on

SET search_path TO siniestro_facil, public;

DO $validation$
DECLARE
    v_missing text[] := ARRAY[]::text[];
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'siniestro_facil'
          AND table_name = 'reportante'
          AND column_name = 'relacion_asegurado'
          AND data_type = 'character varying'
    ) THEN
        v_missing := array_append(v_missing, 'reportante.relacion_asegurado');
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'siniestro_facil'
          AND table_name = 'siniestro'
          AND column_name = 'version'
          AND is_nullable = 'NO'
          AND column_default = '0'
    ) THEN
        v_missing := array_append(v_missing, 'siniestro.version');
    END IF;

    IF to_regclass('siniestro_facil.asignacion_siniestro') IS NULL THEN
        v_missing := array_append(v_missing, 'asignacion_siniestro');
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chk_reportante_relacion_asegurado'
          AND conrelid = 'siniestro_facil.reportante'::regclass
    ) THEN
        v_missing := array_append(v_missing, 'chk_reportante_relacion_asegurado');
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chk_siniestro_version_no_negativa'
          AND conrelid = 'siniestro_facil.siniestro'::regclass
    ) THEN
        v_missing := array_append(v_missing, 'chk_siniestro_version_no_negativa');
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'siniestro_facil'
          AND indexname = 'uq_asignacion_siniestro_activa'
    ) THEN
        v_missing := array_append(v_missing, 'uq_asignacion_siniestro_activa');
    END IF;

    IF cardinality(v_missing) > 0 THEN
        RAISE EXCEPTION 'Validacion fallida. Faltan: %', array_to_string(v_missing, ', ');
    END IF;

    RAISE NOTICE 'OK: migracion Sprint 0 validada estructuralmente.';
END;
$validation$;

SELECT
    (SELECT count(*)
       FROM information_schema.tables
      WHERE table_schema = 'siniestro_facil'
        AND table_type = 'BASE TABLE') AS tablas_totales,
    (SELECT count(*)
       FROM information_schema.columns
      WHERE table_schema = 'siniestro_facil'
        AND table_name IN ('reportante','siniestro')
        AND column_name IN ('relacion_asegurado','version')) AS columnas_nuevas;
