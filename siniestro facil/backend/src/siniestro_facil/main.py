from fastapi import FastAPI

from siniestro_facil import __version__
from siniestro_facil.api.errors import BusinessError, business_error_handler
from siniestro_facil.api.middleware import correlation_id_middleware
from siniestro_facil.api.routes.assistance import router as assistance_router
from siniestro_facil.api.routes.claims import router as claims_router
from siniestro_facil.api.routes.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Siniestro Facil Backend",
        version=__version__,
        docs_url="/docs",
        openapi_url="/openapi.json",
    )
    app.middleware("http")(correlation_id_middleware)
    app.add_exception_handler(BusinessError, business_error_handler)
    app.include_router(health_router)
    app.include_router(claims_router)
    app.include_router(assistance_router)
    return app


app = create_app()

