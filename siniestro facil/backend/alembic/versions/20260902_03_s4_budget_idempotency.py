"""Vínculo e idempotencia de presupuestos S4-BE-02.

Revision ID: 20260902_03
Revises: 20260902_02
"""

from alembic import op


revision = "20260902_03"
down_revision = "20260902_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE siniestro_facil.presupuesto
            ADD COLUMN IF NOT EXISTS id_inspeccion bigint REFERENCES
                siniestro_facil.inspeccion (id_inspeccion)
                ON DELETE RESTRICT;

        CREATE INDEX IF NOT EXISTS idx_presupuesto_inspeccion
            ON siniestro_facil.presupuesto (id_inspeccion);

        CREATE TABLE IF NOT EXISTS
            siniestro_facil.solicitud_presupuesto_idempotente (
                clave varchar(128) PRIMARY KEY,
                huella varchar(64) NOT NULL,
                id_presupuesto bigint NOT NULL UNIQUE REFERENCES
                    siniestro_facil.presupuesto (id_presupuesto)
                    ON DELETE CASCADE,
                respuesta jsonb NOT NULL,
                creado_en timestamptz NOT NULL
                    DEFAULT statement_timestamp(),
                CONSTRAINT chk_solicitud_presupuesto_clave CHECK (
                    char_length(clave) BETWEEN 16 AND 128
                ),
                CONSTRAINT chk_solicitud_presupuesto_huella CHECK (
                    char_length(huella) = 64
                )
            );
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS
            siniestro_facil.solicitud_presupuesto_idempotente;
        DROP INDEX IF EXISTS
            siniestro_facil.idx_presupuesto_inspeccion;
        ALTER TABLE siniestro_facil.presupuesto
            DROP COLUMN IF EXISTS id_inspeccion;
        """
    )
