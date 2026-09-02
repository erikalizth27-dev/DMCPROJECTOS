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


def test_sprint1_revision_persists_idempotency_atomically() -> None:
    revision = (
        BACKEND_ROOT
        / "alembic"
        / "versions"
        / "20260828_01_s1_claim_idempotency.py"
    ).read_text(encoding="utf-8")

    assert 'revision = "20260828_01"' in revision
    assert 'down_revision = "20260825_01"' in revision
    assert "CREATE TABLE IF NOT EXISTS siniestro_facil.solicitud_idempotente" in revision
    assert "id_siniestro bigint NOT NULL UNIQUE" in revision
    assert "DROP TABLE IF EXISTS siniestro_facil.solicitud_idempotente" in revision


def test_sprint1_identity_scope_revision_is_reversible() -> None:
    revision = (
        BACKEND_ROOT
        / "alembic"
        / "versions"
        / "20260828_02_s1_identity_scope.py"
    ).read_text(encoding="utf-8")

    assert 'revision = "20260828_02"' in revision
    assert 'down_revision = "20260828_01"' in revision
    assert "CREATE TABLE IF NOT EXISTS siniestro_facil.identidad_actor" in revision
    assert "num_nonnulls(id_asegurado, id_usuario, id_proveedor) = 1" in revision
    assert "DROP TABLE IF EXISTS siniestro_facil.identidad_actor" in revision


def test_sprint2_evidence_idempotency_revision_is_reversible() -> None:
    revision = (
        BACKEND_ROOT
        / "alembic"
        / "versions"
        / "20260901_01_s2_evidence_idempotency.py"
    ).read_text(encoding="utf-8")

    assert 'revision = "20260901_01"' in revision
    assert 'down_revision = "20260828_02"' in revision
    assert "solicitud_evidencia_idempotente" in revision
    assert "id_evidencia bigint NOT NULL UNIQUE" in revision
    assert "DROP TABLE IF EXISTS" in revision


def test_sprint3_assistance_revision_is_reversible() -> None:
    revision = (
        BACKEND_ROOT
        / "alembic"
        / "versions"
        / "20260902_01_s3_assistance.py"
    ).read_text(encoding="utf-8")

    assert 'revision = "20260902_01"' in revision
    assert 'down_revision = "20260901_01"' in revision
    assert "solicitud_asistencia_idempotente" in revision
    assert "idx_asistencia_siniestro_estado" in revision
    assert "DROP TABLE IF EXISTS" in revision


def test_sprint3_outbox_revision_is_reversible() -> None:
    revision = (
        BACKEND_ROOT
        / "alembic"
        / "versions"
        / "20260902_02_s3_assistance_outbox.py"
    ).read_text(encoding="utf-8")

    assert 'revision = "20260902_02"' in revision
    assert 'down_revision = "20260902_01"' in revision
    assert "CREATE TABLE IF NOT EXISTS siniestro_facil.evento_outbox" in revision
    assert "idx_evento_outbox_pendiente" in revision
    assert "DROP TABLE IF EXISTS siniestro_facil.evento_outbox" in revision


def test_sprint4_budget_revision_is_reversible() -> None:
    revision = (
        BACKEND_ROOT
        / "alembic"
        / "versions"
        / "20260902_03_s4_budget_idempotency.py"
    ).read_text(encoding="utf-8")

    assert 'revision = "20260902_03"' in revision
    assert 'down_revision = "20260902_02"' in revision
    assert "id_inspeccion bigint REFERENCES" in revision
    assert "solicitud_presupuesto_idempotente" in revision
    assert "id_presupuesto bigint NOT NULL UNIQUE" in revision
    assert "DROP TABLE IF EXISTS" in revision
