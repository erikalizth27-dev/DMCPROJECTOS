"""Persistencia e idempotencia de pagos S6-BE-01.

Revision ID: 20260903_04
Revises: 20260903_03
"""

from alembic import op


revision = "20260903_04"
down_revision = "20260903_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE siniestro_facil.pago
            ADD COLUMN id_usuario_prepara bigint REFERENCES
                siniestro_facil.usuario_interno (id_usuario)
                ON DELETE RESTRICT,
            ADD COLUMN version bigint NOT NULL DEFAULT 0;

        CREATE TABLE
            siniestro_facil.solicitud_preparacion_pago_idempotente (
                clave varchar(128) PRIMARY KEY,
                huella varchar(64) NOT NULL,
                id_pago bigint NOT NULL UNIQUE REFERENCES
                    siniestro_facil.pago (id_pago) ON DELETE CASCADE,
                respuesta jsonb NOT NULL,
                creado_en timestamptz NOT NULL DEFAULT statement_timestamp(),
                CONSTRAINT chk_solicitud_preparacion_pago_clave
                    CHECK (char_length(clave) BETWEEN 16 AND 128),
                CONSTRAINT chk_solicitud_preparacion_pago_huella
                    CHECK (char_length(huella) = 64)
            );

        CREATE TABLE
            siniestro_facil.solicitud_autorizacion_pago_idempotente (
                clave varchar(128) PRIMARY KEY,
                huella varchar(64) NOT NULL,
                id_pago bigint NOT NULL UNIQUE REFERENCES
                    siniestro_facil.pago (id_pago) ON DELETE CASCADE,
                respuesta jsonb NOT NULL,
                creado_en timestamptz NOT NULL DEFAULT statement_timestamp(),
                CONSTRAINT chk_solicitud_autorizacion_pago_clave
                    CHECK (char_length(clave) BETWEEN 16 AND 128),
                CONSTRAINT chk_solicitud_autorizacion_pago_huella
                    CHECK (char_length(huella) = 64)
            );

        GRANT SELECT, INSERT
        ON TABLE
            siniestro_facil.solicitud_preparacion_pago_idempotente,
            siniestro_facil.solicitud_autorizacion_pago_idempotente
        TO siniestro_app;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS
            siniestro_facil.solicitud_autorizacion_pago_idempotente;
        DROP TABLE IF EXISTS
            siniestro_facil.solicitud_preparacion_pago_idempotente;
        ALTER TABLE siniestro_facil.pago
            DROP COLUMN IF EXISTS version,
            DROP COLUMN IF EXISTS id_usuario_prepara;
        """
    )
