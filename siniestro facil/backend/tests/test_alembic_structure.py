from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
REVISION = (
    BACKEND_ROOT
    / "alembic"
    / "versions"
    / "20260825_01_sprint0_modelado.py"
)


def test_alembic_configuration_uses_project_source_and_schema() -> None:
    ini = (BACKEND_ROOT / "alembic.ini").read_text(encoding="utf-8")
    env = (BACKEND_ROOT / "alembic" / "env.py").read_text(encoding="utf-8")

    assert "prepend_sys_path = %(here)s/src" in ini
    assert 'os.getenv("DATABASE_URL")' in env
    assert 'version_table_schema="siniestro_facil"' in env


def test_initial_revision_is_idempotent_and_reversible() -> None:
    migration = REVISION.read_text(encoding="utf-8")

    assert 'revision = "20260825_01"' in migration
    assert "down_revision = None" in migration
    assert "ADD COLUMN IF NOT EXISTS relacion_asegurado" in migration
    assert "ADD COLUMN IF NOT EXISTS version" in migration
    assert "CREATE TABLE IF NOT EXISTS siniestro_facil.asignacion_siniestro" in migration
    assert "CREATE UNIQUE INDEX IF NOT EXISTS uq_asignacion_siniestro_activa" in migration
    assert "def downgrade()" in migration
