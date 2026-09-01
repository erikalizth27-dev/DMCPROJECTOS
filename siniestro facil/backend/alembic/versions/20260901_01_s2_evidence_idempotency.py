"""Idempotencia persistente para registro de evidencias S2-BE-03.

Revision ID: 20260901_01
Revises: 20260828_02
"""

from alembic import op


revision = "20260901_01"
down_revision = "20260828_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS
            siniestro_facil.solicitud_evidencia_idempotente (
                clave varchar(128) PRIMARY KEY,
                huella varchar(64) NOT NULL,
                id_evidencia bigint NOT NULL UNIQUE REFERENCES
                    siniestro_facil.evidencia (id_evidencia)
                    ON DELETE CASCADE,
                respuesta jsonb NOT NULL,
                creado_en timestamptz NOT NULL
                    DEFAULT statement_timestamp(),
                CONSTRAINT chk_solicitud_evidencia_clave CHECK (
                    char_length(clave) BETWEEN 16 AND 128
                ),
                CONSTRAINT chk_solicitud_evidencia_huella CHECK (
                    char_length(huella) = 64
                )
            );
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS
            siniestro_facil.solicitud_evidencia_idempotente;
        """
    )
