"""Vinculación de identidad y alcance PostgreSQL para S1-BE-03.

Revision ID: 20260828_02
Revises: 20260828_01
"""

from alembic import op


revision = "20260828_02"
down_revision = "20260828_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS siniestro_facil.identidad_actor (
            subject varchar(255) NOT NULL,
            tenant_id varchar(120) NOT NULL,
            actor_type varchar(20) NOT NULL,
            id_asegurado bigint REFERENCES
                siniestro_facil.asegurado (id_asegurado) ON DELETE CASCADE,
            id_usuario bigint REFERENCES
                siniestro_facil.usuario_interno (id_usuario) ON DELETE CASCADE,
            id_proveedor bigint REFERENCES
                siniestro_facil.proveedor (id_proveedor) ON DELETE CASCADE,
            PRIMARY KEY (subject, tenant_id),
            CONSTRAINT chk_identidad_actor_tipo CHECK (
                actor_type IN ('externo','interno','proveedor')
            ),
            CONSTRAINT chk_identidad_actor_un_destino CHECK (
                num_nonnulls(id_asegurado, id_usuario, id_proveedor) = 1
            )
        );
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS siniestro_facil.identidad_actor;")
