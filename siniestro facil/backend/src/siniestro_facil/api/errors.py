from __future__ import annotations

from uuid import uuid4

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class BusinessError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 422) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


async def business_error_handler(request: Request, exc: BusinessError) -> JSONResponse:
    correlation_id = getattr(request.state, "correlation_id", str(uuid4()))
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "codigo": exc.code,
            "mensaje": exc.message,
            "correlationId": correlation_id,
            "detalles": [],
        },
    )



async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    correlation_id = getattr(
        request.state,
        "correlation_id",
        str(uuid4()),
    )
    details = [
        {
            "campo": ".".join(
                str(part) for part in error.get("loc", ())
                if part != "body"
            ),
            "mensaje": error.get("msg", "Valor inválido"),
            "tipo": error.get("type", "validation_error"),
        }
        for error in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "codigo": "VALIDATION-ERROR",
            "mensaje": "La solicitud contiene valores inválidos",
            "correlationId": correlation_id,
            "detalles": details,
        },
    )
