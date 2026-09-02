"""Idempotencia de decisiones de presupuesto S4-BE-03.

Revision ID: 20260902_04
Revises: 20260902_03
"""

from alembic import op


revision = "20260902_04"
down_revision = "20260902_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS
            siniestro_facil.solicitud_decision_presupuesto_idempotente (
                clave varchar(128) PRIMARY KEY,
                huella varchar(64) NOT NULL,
                id_cambio bigint NOT NULL UNIQUE REFERENCES
                    siniestro_facil.cambio_presupuesto (id_cambio)
                    ON DELETE CASCADE,
                respuesta jsonb NOT NULL,
                creado_en timestamptz NOT NULL
                    DEFAULT statement_timestamp(),
                CONSTRAINT chk_solicitud_decision_presupuesto_clave CHECK (
                    char_length(clave) BETWEEN 16 AND 128
                ),
                CONSTRAINT chk_solicitud_decision_presupuesto_huella CHECK (
                    char_length(huella) = 64
                )
            );
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS
            siniestro_facil.solicitud_decision_presupuesto_idempotente;
        """
    )
