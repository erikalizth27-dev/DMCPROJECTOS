\set ON_ERROR_STOP on

BEGIN;
SET LOCAL search_path TO siniestro_facil, public;

ALTER TABLE reportante
    ADD COLUMN IF NOT EXISTS relacion_asegurado varchar(30);

DO $migration$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chk_reportante_relacion_asegurado'
          AND conrelid = 'siniestro_facil.reportante'::regclass
    ) THEN
        ALTER TABLE reportante
            ADD CONSTRAINT chk_reportante_relacion_asegurado CHECK (
                (es_titular AND relacion_asegurado IS NULL)
                OR
                (NOT es_titular AND relacion_asegurado IN (
                    'familiar','dependiente','testigo','otro'
                ))
            );
    END IF;
END;
$migration$;

ALTER TABLE siniestro
    ADD COLUMN IF NOT EXISTS version bigint NOT NULL DEFAULT 0;

DO $migration$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chk_siniestro_version_no_negativa'
          AND conrelid = 'siniestro_facil.siniestro'::regclass
    ) THEN
        ALTER TABLE siniestro
            ADD CONSTRAINT chk_siniestro_version_no_negativa CHECK (version >= 0);
    END IF;
END;
$migration$;

CREATE TABLE IF NOT EXISTS asignacion_siniestro (
    id_asignacion bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_siniestro bigint NOT NULL
        REFERENCES siniestro (id_siniestro) ON DELETE CASCADE,
    id_usuario bigint NOT NULL
        REFERENCES usuario_interno (id_usuario) ON DELETE RESTRICT,
    motivo text NOT NULL,
    asignado_en timestamptz NOT NULL DEFAULT statement_timestamp(),
    finalizado_en timestamptz,
    CONSTRAINT chk_asignacion_motivo_no_vacio CHECK (btrim(motivo) <> ''),
    CONSTRAINT chk_asignacion_fechas CHECK (
        finalizado_en IS NULL OR finalizado_en >= asignado_en
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_asignacion_siniestro_activa
    ON asignacion_siniestro (id_siniestro)
    WHERE finalizado_en IS NULL;

CREATE INDEX IF NOT EXISTS idx_asignacion_usuario
    ON asignacion_siniestro (id_usuario, asignado_en DESC);

COMMIT;

