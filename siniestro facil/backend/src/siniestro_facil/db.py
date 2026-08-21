from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from .config import Settings


def create_database_engine(settings: Settings) -> Engine:
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL no configurada")
    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
    )

