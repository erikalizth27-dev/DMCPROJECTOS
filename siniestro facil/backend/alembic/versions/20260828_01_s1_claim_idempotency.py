"""Persistencia idempotente del registro de siniestros de Sprint 1.

Revision ID: 20260828_01
Revises: 20260825_01
"""

from alembic import op


revision = "20260828_01"
down_revision = "20260825_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS siniestro_facil.solicitud_idempotente (
            clave varchar(128) PRIMARY KEY,
            huella varchar(64) NOT NULL,
            id_siniestro bigint NOT NULL UNIQUE REFERENCES
                siniestro_facil.siniestro (id_siniestro) ON DELETE CASCADE,
            respuesta jsonb NOT NULL,
            creado_en timestamptz NOT NULL DEFAULT statement_timestamp(),
            CONSTRAINT chk_solicitud_idempotente_clave
                CHECK (char_length(clave) BETWEEN 16 AND 128),
            CONSTRAINT chk_solicitud_idempotente_huella
                CHECK (char_length(huella) = 64)
        );
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS siniestro_facil.solicitud_idempotente;")
