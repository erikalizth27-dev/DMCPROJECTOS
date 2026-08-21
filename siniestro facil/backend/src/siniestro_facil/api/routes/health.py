from fastapi import APIRouter, Depends

from siniestro_facil.config import Settings

router = APIRouter(prefix="/health", tags=["Technical"])


def get_settings() -> Settings:
    return Settings.from_environment()


@router.get("/live")
def live(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name, "version": settings.app_version}


@router.get("/ready")
def ready(settings: Settings = Depends(get_settings)) -> dict[str, object]:
    errors = settings.readiness_errors()
    return {"status": "ready" if not errors else "not_ready", "errors": errors}

