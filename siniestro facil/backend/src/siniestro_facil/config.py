from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    app_env: str = "local"
    app_name: str = "Siniestro Facil Backend"
    app_version: str = "0.1.0"
    database_url: str | None = None
    database_schema: str = "siniestro_facil"
    log_level: str = "INFO"

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls(
            app_env=os.getenv("APP_ENV", "local"),
            app_name=os.getenv("APP_NAME", "Siniestro Facil Backend"),
            app_version=os.getenv("APP_VERSION", "0.1.0"),
            database_url=os.getenv("DATABASE_URL"),
            database_schema=os.getenv("DATABASE_SCHEMA", "siniestro_facil"),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        )

    def readiness_errors(self) -> list[str]:
        errors: list[str] = []
        if not self.database_url:
            errors.append("DATABASE_URL no configurada")
        if self.database_schema != "siniestro_facil":
            errors.append("DATABASE_SCHEMA debe ser siniestro_facil")
        return errors

