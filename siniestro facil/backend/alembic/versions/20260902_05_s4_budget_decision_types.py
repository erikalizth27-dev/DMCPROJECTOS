"""Tipos formales de decisión de presupuesto S4-BE-03.

Revision ID: 20260902_05
Revises: 20260902_04
"""

from alembic import op


revision = "20260902_05"
down_revision = "20260902_04"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE siniestro_facil.cambio_presupuesto
            DROP CONSTRAINT IF EXISTS chk_cambio_tipo;
        ALTER TABLE siniestro_facil.cambio_presupuesto
            ADD CONSTRAINT chk_cambio_tipo CHECK (
                tipo_cambio IN (
                    'observacion', 'repuesto_alternativo', 'ampliacion',
                    'aprobacion', 'rechazo'
                )
            );
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM siniestro_facil.cambio_presupuesto
        WHERE tipo_cambio IN ('aprobacion', 'rechazo');
        ALTER TABLE siniestro_facil.cambio_presupuesto
            DROP CONSTRAINT IF EXISTS chk_cambio_tipo;
        ALTER TABLE siniestro_facil.cambio_presupuesto
            ADD CONSTRAINT chk_cambio_tipo CHECK (
                tipo_cambio IN (
                    'observacion', 'repuesto_alternativo', 'ampliacion'
                )
            );
        """
    )
