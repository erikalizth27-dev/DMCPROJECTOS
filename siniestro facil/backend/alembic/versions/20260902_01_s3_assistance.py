"""Persistencia e idempotencia de asistencia S3-BE-01.

Revision ID: 20260902_01
Revises: 20260901_01
"""

from alembic import op


revision = "20260902_01"
down_revision = "20260901_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE siniestro_facil.asistencia
            DROP CONSTRAINT IF EXISTS chk_asistencia_estado;

        ALTER TABLE siniestro_facil.asistencia
            ADD COLUMN IF NOT EXISTS tipo_asistencia varchar(50),
            ADD COLUMN IF NOT EXISTS motivo text,
            ADD COLUMN IF NOT EXISTS referencia_externa varchar(120),
            ADD COLUMN IF NOT EXISTS creado_en timestamptz
                NOT NULL DEFAULT statement_timestamp(),
            ADD COLUMN IF NOT EXISTS actualizado_en timestamptz
                NOT NULL DEFAULT statement_timestamp();

        UPDATE siniestro_facil.asistencia
        SET tipo_asistencia = COALESCE(tipo_asistencia, 'grua'),
            motivo = COALESCE(motivo, 'registro_previo_sprint_3');

        ALTER TABLE siniestro_facil.asistencia
            ALTER COLUMN tipo_asistencia SET NOT NULL,
            ALTER COLUMN motivo SET NOT NULL;

        ALTER TABLE siniestro_facil.asistencia
            ADD CONSTRAINT chk_asistencia_estado CHECK (
                estado_solicitud IN (
                    'pendiente', 'enviada', 'aceptada', 'rechazada',
                    'sin_respuesta', 'escalada', 'cancelada'
                )
            );

        CREATE TABLE IF NOT EXISTS
            siniestro_facil.solicitud_asistencia_idempotente (
                clave varchar(128) PRIMARY KEY,
                huella varchar(64) NOT NULL,
                id_asistencia bigint NOT NULL UNIQUE REFERENCES
                    siniestro_facil.asistencia (id_asistencia)
                    ON DELETE CASCADE,
                respuesta jsonb NOT NULL,
                creado_en timestamptz NOT NULL
                    DEFAULT statement_timestamp(),
                CONSTRAINT chk_solicitud_asistencia_clave CHECK (
                    char_length(clave) BETWEEN 16 AND 128
                ),
                CONSTRAINT chk_solicitud_asistencia_huella CHECK (
                    char_length(huella) = 64
                )
            );

        CREATE INDEX IF NOT EXISTS idx_asistencia_siniestro_estado
            ON siniestro_facil.asistencia
                (id_siniestro, estado_solicitud);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS
            siniestro_facil.idx_asistencia_siniestro_estado;
        DROP TABLE IF EXISTS
            siniestro_facil.solicitud_asistencia_idempotente;

        UPDATE siniestro_facil.asistencia
        SET estado_solicitud = 'sin_respuesta'
        WHERE estado_solicitud NOT IN (
            'aceptada', 'rechazada', 'sin_respuesta'
        );

        ALTER TABLE siniestro_facil.asistencia
            DROP CONSTRAINT IF EXISTS chk_asistencia_estado,
            DROP COLUMN IF EXISTS tipo_asistencia,
            DROP COLUMN IF EXISTS motivo,
            DROP COLUMN IF EXISTS referencia_externa,
            DROP COLUMN IF EXISTS creado_en,
            DROP COLUMN IF EXISTS actualizado_en;

        ALTER TABLE siniestro_facil.asistencia
            ADD CONSTRAINT chk_asistencia_estado CHECK (
                estado_solicitud IN (
                    'aceptada', 'rechazada', 'sin_respuesta'
                )
            );
        """
    )
