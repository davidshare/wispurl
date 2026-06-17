"""Rate limiter application factory.

Wires configuration, structured logging, the async Redis client lifespan,
request-correlation middleware, exception handlers, and the ``/check`` router.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from uuid import uuid4

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from redis.asyncio import Redis
from starlette.responses import Response as StarletteResponse

from app.config import get_settings
from app.errors.exceptions import (
    RateLimiterDomainError,
    domain_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.routes.check import router as check_router
from shared.logging_config import (
    bind_request_id,
    clear_request_context,
    configure_logging,
)

logger = structlog.get_logger()


async def handle_domain_error(request: Request, exc: Exception) -> StarletteResponse:
    """Dispatch a rate limiter domain error to its handler; fall back to 500."""
    if isinstance(exc, RateLimiterDomainError):
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


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Open one shared async Redis client for the process lifetime."""
    settings = get_settings()
    redis: Redis = Redis.from_url(settings.redis_url, decode_responses=True)
    app.state.redis = redis
    logger.info("rate_limiter_started")
    try:
        yield
    finally:
        await redis.aclose()


def create_app() -> FastAPI:
    """Build and configure the rate limiter ``FastAPI`` application."""
    settings = get_settings()
    configure_logging("rate-limiter-service", settings.log_level)

    app = FastAPI(
        title="Rate Limiter Service",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
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

    app.add_exception_handler(RateLimiterDomainError, handle_domain_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    app.include_router(check_router)

    @app.get("/health", status_code=status.HTTP_200_OK, tags=["health"])
    async def health() -> JSONResponse:
        """Readiness probe verifying Redis connectivity."""
        redis: Redis = app.state.redis
        await redis.ping()
        return JSONResponse({"status": "ok"})

    logger.info("rate_limiter_configured")
    return app


app = create_app()
