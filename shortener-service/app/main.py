from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from uuid import uuid4

import httpx
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
    ShortenerDomainError,
    domain_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.routes.links import router as links_router
from app.routes.redirect import router as redirect_router
from shared import messaging
from shared.logging_config import (
    bind_request_id,
    clear_request_context,
    configure_logging,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Open one shared ``httpx.AsyncClient`` for fire-and-forget analytics calls.

    A single pooled client lives for the process lifetime so the per-click
    background task that reports to Analytics does not pay connection setup each
    time. Its timeout is bounded by ``ANALYTICS_REQUEST_TIMEOUT`` so a slow or down
    Analytics service can never delay the redirect path.
    """
    settings = get_settings()
    timeout = httpx.Timeout(settings.analytics_request_timeout)
    async with httpx.AsyncClient(timeout=timeout) as client:
        app.state.http_client = client
        app.state.event_publisher = None
        connection = None
        if settings.events_publish_enabled:
            try:
                connection = await messaging.connect(settings.rabbitmq_url)
                app.state.event_publisher = await messaging.create_publisher(
                    connection,
                )
            except Exception as exc:
                # Degrade gracefully: the redirect's publish is fire-and-forget, so
                # a broker that is down at startup must not stop the service.
                logger.warning("event_publisher_unavailable", error=str(exc))
        try:
            yield
        finally:
            if connection is not None:
                await connection.close()


async def handle_domain_error(request: Request, exc: Exception) -> StarletteResponse:
    if isinstance(exc, ShortenerDomainError):
        return await domain_exception_handler(request, exc)
    return await unhandled_exception_handler(request, exc)


async def handle_validation_error(
    request: Request,
    exc: Exception,
) -> StarletteResponse:
    if isinstance(exc, RequestValidationError):
        return await validation_exception_handler(request, exc)
    return await unhandled_exception_handler(request, exc)


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging("shortener-service", settings.log_level)

    app = FastAPI(
        title="Shortener Service",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )

    @app.middleware("http")
    async def request_context_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        bind_request_id(request_id)
        try:
            response = await call_next(request)
        finally:
            clear_request_context()
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        if request.url.path.startswith("/v1/links"):
            response.headers["Cache-Control"] = "no-store"
        return response

    app.add_exception_handler(ShortenerDomainError, handle_domain_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    app.include_router(links_router)

    @app.get("/health", status_code=status.HTTP_200_OK, tags=["health"])
    async def health() -> JSONResponse:
        async with SessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return JSONResponse({"status": "ok"})

    app.include_router(redirect_router)

    logger.info("shortener_service_configured")
    return app


app = create_app()
