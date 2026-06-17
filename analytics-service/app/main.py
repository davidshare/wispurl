"""Analytics application factory.

Wires configuration, structured logging, request-correlation middleware, exception
handlers, and the events/stats routers.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from uuid import uuid4

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from sqlalchemy import text
from starlette.responses import Response as StarletteResponse

from app.config import get_settings
from app.database import SessionLocal
from app.errors.exceptions import (
    AnalyticsDomainError,
    domain_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.routes.events import router as events_router
from app.routes.stats import router as stats_router
from shared.logging_config import (
    bind_request_id,
    clear_request_context,
    configure_logging,
)

logger = structlog.get_logger()


async def handle_domain_error(request: Request, exc: Exception) -> StarletteResponse:
    """Dispatch an analytics domain error to its handler; fall back to 500."""
    if isinstance(exc, AnalyticsDomainError):
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
    """Build and configure the analytics ``FastAPI`` application."""
    settings = get_settings()
    configure_logging("analytics-service", settings.log_level)

    app = FastAPI(
        title="Analytics Service",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
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
        if request.url.path.startswith("/stats"):
            response.headers["Cache-Control"] = "no-store"
        return response

    app.add_exception_handler(AnalyticsDomainError, handle_domain_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    app.include_router(events_router)
    app.include_router(stats_router)

    @app.get("/health", status_code=status.HTTP_200_OK, tags=["health"])
    async def health() -> JSONResponse:
        """Readiness probe verifying database connectivity."""
        async with SessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return JSONResponse({"status": "ok"})

    logger.info("analytics_service_configured")
    return app


app = create_app()
