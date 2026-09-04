from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCKERFILE = (ROOT / "Dockerfile").read_text(encoding="utf-8")
DOCKERIGNORE = (ROOT / ".dockerignore").read_text(encoding="utf-8")


def test_uses_approved_python_runtime() -> None:
    assert DOCKERFILE.startswith("FROM python:3.12-slim")


def test_runs_as_non_root_user() -> None:
    assert "useradd --uid 10001" in DOCKERFILE
    assert "USER 10001:10001" in DOCKERFILE


def test_installs_runtime_and_gcp_dependencies() -> None:
    assert 'python -m pip install ".[gcp]"' in DOCKERFILE


def test_listens_on_cloud_run_port() -> None:
    assert "PORT=8080" in DOCKERFILE
    assert "--port ${PORT:-8080}" in DOCKERFILE


def test_exec_preserves_termination_signals() -> None:
    assert "exec uvicorn siniestro_facil.main:app" in DOCKERFILE


def test_image_contains_alembic_for_exclusive_migration_job() -> None:
    assert "COPY alembic.ini ./" in DOCKERFILE
    assert "COPY alembic ./alembic" in DOCKERFILE


def test_build_context_excludes_secrets_and_development_files() -> None:
    ignored = set(DOCKERIGNORE.splitlines())
    assert ".env" in ignored
    assert ".venv" in ignored
    assert ".git" in ignored
    assert "tests" in ignored
    assert "scripts" in ignored
