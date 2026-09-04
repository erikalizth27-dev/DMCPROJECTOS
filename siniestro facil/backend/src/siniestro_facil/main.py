from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from siniestro_facil import __version__
from siniestro_facil.api.errors import (
    BusinessError,
    business_error_handler,
    validation_error_handler,
)
from siniestro_facil.api.middleware import correlation_id_middleware
from siniestro_facil.api.routes.assistance import router as assistance_router
from siniestro_facil.api.routes.claims import router as claims_router
from siniestro_facil.api.routes.health import router as health_router
from siniestro_facil.api.routes.fraud import router as fraud_router
from siniestro_facil.api.routes.inspections import router as inspections_router
from siniestro_facil.api.routes.payments import router as payments_router
from siniestro_facil.api.routes.relations import router as relations_router
from siniestro_facil.api.routes.timeline import router as timeline_router
from siniestro_facil.api.routes.metrics import router as metrics_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Siniestro Facil Backend",
        version=__version__,
        docs_url="/docs",
        openapi_url="/openapi.json",
    )
    app.middleware("http")(correlation_id_middleware)
    app.add_exception_handler(BusinessError, business_error_handler)
    app.add_exception_handler(
        RequestValidationError,
        validation_error_handler,
    )
    app.include_router(health_router)
    app.include_router(claims_router)
    app.include_router(assistance_router)
    app.include_router(inspections_router)
    app.include_router(fraud_router)
    app.include_router(relations_router)
    app.include_router(payments_router)
    app.include_router(timeline_router)
    app.include_router(metrics_router)
    return app


app = create_app()

