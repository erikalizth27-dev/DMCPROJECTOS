from __future__ import annotations

import json
import logging
import sys
from functools import lru_cache
from typing import Any


LOGGER_NAME = "siniestro_facil.http"


class JsonLineFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = record.msg
        if not isinstance(payload, dict):
            payload = {
                "severity": record.levelname,
                "message": "application_log",
            }
        return json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )


@lru_cache(maxsize=1)
def http_logger() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonLineFormatter())
        logger.addHandler(handler)
    return logger


def build_http_log(
    *,
    correlation_id: str,
    method: str,
    path: str,
    status_code: int,
    latency_seconds: float,
    severity: str = "INFO",
) -> dict[str, Any]:
    return {
        "severity": severity,
        "message": "http_request",
        "event": "http_request",
        "correlationId": correlation_id,
        "httpRequest": {
            "requestMethod": method,
            "requestUrl": path,
            "status": status_code,
            "latency": f"{max(latency_seconds, 0.0):.6f}s",
        },
    }
