"""QR application factory.

Wires configuration, structured logging, request-correlation middleware, exception
handlers, and the QR router. The service is stateless: no database, no lifespan
resources, nothing per-request is persisted.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from uuid import uuid4

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from starlette.responses import Response as StarletteResponse

from app.config import get_settings
from app.errors.exceptions import (
    QrDomainError,
    domain_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.routes.qr import router as qr_router
from shared.logging_config import (
    bind_request_id,
    clear_request_context,
    configure_logging,
)

logger = structlog.get_logger()


async def handle_domain_error(request: Request, exc: Exception) -> StarletteResponse:
    """Dispatch a QR domain error to its handler; fall back to 500."""
    if isinstance(exc, QrDomainError):
        return await domain_exception_handler(request, exc)
    return await unhandled_exception_handler(request, exc)


async def handle_validation_error(
    request: Request,
    exc: Exception,
) -> StarletteResponse:
    """Dispatch a request-validation error to its handler; fall back to 500."""
    if isinstance(exc, RequestValidationError):
        return await validation_exception_handler(request, exc)
    return await unhandled_exception_handler(request, exc)


def create_app() -> FastAPI:
    """Build and configure the QR ``FastAPI`` application."""
    settings = get_settings()
    configure_logging("qr-service", settings.log_level)

    app = FastAPI(
        title="QR Code Service",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    @app.middleware("http")
    async def request_context_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Bind the forwarded ``X-Request-ID`` for logging and add safety headers."""
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        bind_request_id(request_id)
        try:
            response = await call_next(request)
        finally:
            clear_request_context()
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    app.add_exception_handler(QrDomainError, handle_domain_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    app.include_router(qr_router)

    @app.get("/health", status_code=status.HTTP_200_OK, tags=["health"])
    async def health() -> JSONResponse:
        """Liveness probe (stateless service — nothing to check but the process)."""
        return JSONResponse({"status": "ok"})

    logger.info("qr_service_configured")
    return app


app = create_app()
