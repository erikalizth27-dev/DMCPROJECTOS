from __future__ import annotations

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

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


def database_readiness_errors(engine: Engine, schema: str) -> list[str]:
    """Comprueba conectividad y existencia del esquema sin exponer detalles sensibles."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            schema_found = connection.execute(
                text("SELECT to_regnamespace(:schema)"), {"schema": schema}
            ).scalar_one_or_none()
    except SQLAlchemyError:
        return ["No fue posible conectar con PostgreSQL"]

    if schema_found is None:
        return [f"El esquema requerido {schema} no existe"]
    return []
