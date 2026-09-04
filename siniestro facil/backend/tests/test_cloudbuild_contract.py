from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "cloudbuild.yaml"
SCRIPT = (ROOT / "scripts/29_submit_platform_build.sh").read_text(
    encoding="utf-8"
)
CONFIG = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def steps() -> dict[str, dict[str, object]]:
    return {step["id"]: step for step in CONFIG["steps"]}


def test_pipeline_uses_cloud_logging_without_implicit_bucket() -> None:
    assert CONFIG["options"]["logging"] == "CLOUD_LOGGING_ONLY"


def test_pipeline_runs_tests_before_build() -> None:
    ordered = [step["id"] for step in CONFIG["steps"]]
    assert ordered[:3] == ["test", "build", "push"]
    assert "python -m pytest -q" in CONFIG["steps"][0]["args"][-1]


def test_image_is_tagged_from_required_substitution() -> None:
    assert CONFIG["substitutions"]["_IMAGE_TAG"] == "manual"
    assert "$_IMAGE_TAG" in str(CONFIG["steps"][1])
    assert "git rev-parse --short=12 HEAD" in SCRIPT


def test_migration_precedes_deployment() -> None:
    ordered = [step["id"] for step in CONFIG["steps"]]
    assert ordered.index("configure-migration") < ordered.index("migrate")
    assert ordered.index("migrate") < ordered.index("deploy")


def test_migration_is_exclusive_cloud_run_job() -> None:
    migration = steps()["migrate"]
    assert migration["entrypoint"] == "gcloud"
    assert "jobs" in migration["args"]
    assert "execute" in migration["args"]
    assert "--wait" in migration["args"]


def test_service_is_updated_only_after_successful_migration() -> None:
    deploy = steps()["deploy"]
    assert "services" in deploy["args"]
    assert "update" in deploy["args"]


def test_private_smoke_checks_both_health_endpoints() -> None:
    smoke = str(steps()["smoke"])
    assert "gcloud auth print-identity-token" in smoke
    assert "/health/live" in smoke
    assert "/health/ready" in smoke


def test_submission_requires_dedicated_deployer_identity() -> None:
    assert "--service-account=" in SCRIPT
    assert "siniestro-deployer-piloto@" in SCRIPT
