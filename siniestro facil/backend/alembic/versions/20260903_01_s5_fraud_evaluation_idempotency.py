"""Idempotencia persistente para evaluación antifraude S5-BE-01.

Revision ID: 20260903_01
Revises: 20260902_05
"""

from alembic import op


revision = "20260903_01"
down_revision = "20260902_05"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE siniestro_facil.solicitud_evaluacion_fraude_idempotente (
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

        CREATE INDEX idx_solicitud_evaluacion_fraude_siniestro
            ON siniestro_facil.solicitud_evaluacion_fraude_idempotente
                (id_siniestro, creado_en);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS
            siniestro_facil.solicitud_evaluacion_fraude_idempotente;
        """
    )
