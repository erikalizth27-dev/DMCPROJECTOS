"""Ajustes de modelado acordados para Sprint 0.

Revision ID: 20260825_01
Revises: None
"""

from alembic import op


revision = "20260825_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Se conserva idempotencia porque el SQL 05 pudo haberse aplicado manualmente.
    op.execute(
        """
        ALTER TABLE siniestro_facil.reportante
            ADD COLUMN IF NOT EXISTS relacion_asegurado varchar(30);

        DO $migration$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'chk_reportante_relacion_asegurado'
                  AND conrelid = 'siniestro_facil.reportante'::regclass
            ) THEN
                ALTER TABLE siniestro_facil.reportante
                    ADD CONSTRAINT chk_reportante_relacion_asegurado CHECK (
                        (es_titular AND relacion_asegurado IS NULL)
                        OR (NOT es_titular AND relacion_asegurado IN
                            ('familiar','dependiente','testigo','otro'))
                    );
            END IF;
        END;
        $migration$;

        ALTER TABLE siniestro_facil.siniestro
            ADD COLUMN IF NOT EXISTS version bigint NOT NULL DEFAULT 0;

        DO $migration$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'chk_siniestro_version_no_negativa'
                  AND conrelid = 'siniestro_facil.siniestro'::regclass
            ) THEN
                ALTER TABLE siniestro_facil.siniestro
                    ADD CONSTRAINT chk_siniestro_version_no_negativa
                    CHECK (version >= 0);
            END IF;
        END;
        $migration$;

        CREATE TABLE IF NOT EXISTS siniestro_facil.asignacion_siniestro (
            id_asignacion bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            id_siniestro bigint NOT NULL REFERENCES
                siniestro_facil.siniestro (id_siniestro) ON DELETE CASCADE,
            id_usuario bigint NOT NULL REFERENCES
                siniestro_facil.usuario_interno (id_usuario) ON DELETE RESTRICT,
            motivo text NOT NULL,
            asignado_en timestamptz NOT NULL DEFAULT statement_timestamp(),
            finalizado_en timestamptz,
            CONSTRAINT chk_asignacion_motivo_no_vacio
                CHECK (btrim(motivo) <> ''),
            CONSTRAINT chk_asignacion_fechas
                CHECK (finalizado_en IS NULL OR finalizado_en >= asignado_en)
        );

        CREATE UNIQUE INDEX IF NOT EXISTS uq_asignacion_siniestro_activa
            ON siniestro_facil.asignacion_siniestro (id_siniestro)
            WHERE finalizado_en IS NULL;

        CREATE INDEX IF NOT EXISTS idx_asignacion_usuario
            ON siniestro_facil.asignacion_siniestro
            (id_usuario, asignado_en DESC);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS siniestro_facil.asignacion_siniestro;
        ALTER TABLE siniestro_facil.siniestro
            DROP COLUMN IF EXISTS version;
        ALTER TABLE siniestro_facil.reportante
            DROP COLUMN IF EXISTS relacion_asegurado;
        """
    )
