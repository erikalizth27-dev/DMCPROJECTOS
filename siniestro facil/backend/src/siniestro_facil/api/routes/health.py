from functools import lru_cache

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.engine import Engine

from siniestro_facil.config import Settings
from siniestro_facil.db import create_database_engine, database_readiness_errors

router = APIRouter(prefix="/health", tags=["Technical"])


def get_settings() -> Settings:
    return Settings.from_environment()


@lru_cache(maxsize=1)
def _cached_engine(database_url: str, database_schema: str) -> Engine:
    return create_database_engine(
        Settings(database_url=database_url, database_schema=database_schema)
    )


def get_engine(settings: Settings = Depends(get_settings)) -> Engine:
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL no configurada")
    return _cached_engine(settings.database_url, settings.database_schema)


@router.get("/live")
def live(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name, "version": settings.app_version}


@router.get("/ready", responses={503: {"description": "Dependencias no disponibles"}})
def ready(settings: Settings = Depends(get_settings)) -> JSONResponse:
    errors = settings.readiness_errors()
    if not errors and settings.database_url:
        engine = _cached_engine(settings.database_url, settings.database_schema)
        errors.extend(database_readiness_errors(engine, settings.database_schema))
    status_code = 200 if not errors else 503
    return JSONResponse(
        status_code=status_code,
        content={"status": "ready" if not errors else "not_ready", "errors": errors},
    )
