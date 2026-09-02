"""Outbox transaccional para mensajería de asistencia S3-BE-03.

Revision ID: 20260902_02
Revises: 20260902_01
"""

from alembic import op


revision = "20260902_02"
down_revision = "20260902_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS siniestro_facil.evento_outbox (
            id_evento_outbox bigint GENERATED ALWAYS AS IDENTITY
                PRIMARY KEY,
            event_id varchar(36) NOT NULL UNIQUE,
            aggregate_type varchar(50) NOT NULL,
            aggregate_id bigint NOT NULL,
            event_type varchar(80) NOT NULL,
            payload jsonb NOT NULL,
            estado varchar(20) NOT NULL DEFAULT 'pendiente',
            intentos bigint NOT NULL DEFAULT 0,
            ocurrido_en timestamptz NOT NULL,
            disponible_en timestamptz NOT NULL,
            publicado_en timestamptz,
            pubsub_message_id varchar(255),
            ultimo_error text,
            CONSTRAINT chk_evento_outbox_estado CHECK (
                estado IN (
                    'pendiente', 'publicando', 'publicado', 'fallido'
                )
            ),
            CONSTRAINT chk_evento_outbox_intentos CHECK (
                intentos >= 0
            )
        );

        CREATE INDEX IF NOT EXISTS idx_evento_outbox_pendiente
            ON siniestro_facil.evento_outbox
                (estado, disponible_en, id_evento_outbox)
            WHERE estado IN ('pendiente', 'fallido');
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS
            siniestro_facil.idx_evento_outbox_pendiente;
        DROP TABLE IF EXISTS siniestro_facil.evento_outbox;
        """
    )
