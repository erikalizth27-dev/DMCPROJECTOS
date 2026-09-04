from __future__ import annotations

import re
from time import perf_counter
from uuid import uuid4

from fastapi import Request

from siniestro_facil.observability import build_http_log, http_logger


CORRELATION_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")


def normalized_correlation_id(value: str | None) -> str:
    candidate = (value or "").strip()
    if CORRELATION_ID_PATTERN.fullmatch(candidate):
        return candidate
    return str(uuid4())


async def correlation_id_middleware(request: Request, call_next):
    correlation_id = normalized_correlation_id(
        request.headers.get("X-Correlation-ID")
    )
    request.state.correlation_id = correlation_id
    started_at = perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        http_logger().error(
            build_http_log(
                correlation_id=correlation_id,
                method=request.method,
                path=request.url.path,
                status_code=500,
                latency_seconds=perf_counter() - started_at,
                severity="ERROR",
            )
        )
        raise

    response.headers["X-Correlation-ID"] = correlation_id
    severity = "ERROR" if response.status_code >= 500 else "INFO"
    http_logger().log(
        40 if severity == "ERROR" else 20,
        build_http_log(
            correlation_id=correlation_id,
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            latency_seconds=perf_counter() - started_at,
            severity=severity,
        ),
    )
    return response
