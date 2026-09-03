"""Persistencia de revisión humana antifraude S5-BE-02.

Revision ID: 20260903_02
Revises: 20260903_01
"""

from alembic import op


revision = "20260903_02"
down_revision = "20260903_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE siniestro_facil.alerta
            ADD COLUMN version bigint NOT NULL DEFAULT 0;

        CREATE TABLE siniestro_facil.solicitud_revision_alerta_idempotente (
            clave varchar(128) PRIMARY KEY,
            huella varchar(64) NOT NULL,
            id_alerta bigint NOT NULL UNIQUE REFERENCES
                siniestro_facil.alerta (id_alerta) ON DELETE CASCADE,
            respuesta jsonb NOT NULL,
            creado_en timestamptz NOT NULL DEFAULT statement_timestamp(),
            CONSTRAINT chk_solicitud_revision_alerta_clave
                CHECK (char_length(clave) BETWEEN 16 AND 128),
            CONSTRAINT chk_solicitud_revision_alerta_huella
                CHECK (char_length(huella) = 64)
        );
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS
            siniestro_facil.solicitud_revision_alerta_idempotente;
        ALTER TABLE siniestro_facil.alerta
            DROP COLUMN IF EXISTS version;
        """
    )
