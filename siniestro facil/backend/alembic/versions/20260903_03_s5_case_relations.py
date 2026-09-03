"""Persistencia de relaciones exactas S5-BE-03.

Revision ID: 20260903_03
Revises: 20260903_02
"""

from alembic import op


revision = "20260903_03"
down_revision = "20260903_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE siniestro_facil.relacion_casos
            ADD COLUMN valor_normalizado varchar(255),
            ADD COLUMN estado_revision varchar(25) NOT NULL
                DEFAULT 'pendiente_revision';

        CREATE UNIQUE INDEX uq_relacion_casos_par_criterio
            ON siniestro_facil.relacion_casos
                (id_siniestro_a, id_siniestro_b, criterio_relacion);

        CREATE TABLE siniestro_facil.solicitud_relacion_casos_idempotente (
            clave varchar(128) PRIMARY KEY,
            huella varchar(64) NOT NULL,
            id_siniestro bigint NOT NULL REFERENCES
                siniestro_facil.siniestro (id_siniestro) ON DELETE CASCADE,
            respuesta jsonb NOT NULL,
            creado_en timestamptz NOT NULL DEFAULT statement_timestamp(),
            CONSTRAINT chk_solicitud_relacion_casos_clave
                CHECK (char_length(clave) BETWEEN 16 AND 128),
            CONSTRAINT chk_solicitud_relacion_casos_huella
                CHECK (char_length(huella) = 64)
        );
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS
            siniestro_facil.solicitud_relacion_casos_idempotente;
        DROP INDEX IF EXISTS
            siniestro_facil.uq_relacion_casos_par_criterio;
        ALTER TABLE siniestro_facil.relacion_casos
            DROP COLUMN IF EXISTS estado_revision,
            DROP COLUMN IF EXISTS valor_normalizado;
        """
    )
