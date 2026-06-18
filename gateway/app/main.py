"""Gateway application factory.

Wires together configuration, structured logging, the shared HTTP client lifespan,
request-correlation middleware, exception handlers, and the proxy routers. Route
registration ORDER is significant — see :func:`create_app`.
"""

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
from starlette.responses import Response as StarletteResponse

from app.config import get_settings
from app.errors.exceptions import (
    GatewayDomainError,
    domain_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.routes.auth import router as auth_router
from app.routes.links import router as links_router
from app.routes.qr import router as qr_router
from app.routes.redirect import router as redirect_router
from app.routes.stats import router as stats_router
from shared.logging_config import (
    bind_request_id,
    clear_request_context,
    configure_logging,
)

logger = structlog.get_logger()


async def handle_domain_error(request: Request, exc: Exception) -> StarletteResponse:
    """Dispatch a gateway domain error to its handler; fall back to 500 otherwise."""
    if isinstance(exc, GatewayDomainError):
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
    """Open one shared ``httpx.AsyncClient`` for the process lifetime.

    A single pooled client is created at startup and closed at shutdown. It is
    configured with ``follow_redirects=False`` so upstream 3xx responses (notably
    the Shortener's 307) are relayed to the client instead of followed here, and
    with explicit connect/read timeouts so no upstream call can hang indefinitely.
    """
    settings = get_settings()
    timeout = httpx.Timeout(
        connect=settings.request_connect_timeout,
        read=settings.request_read_timeout,
        write=settings.request_read_timeout,
        pool=settings.request_connect_timeout,
    )
    # Bound the upstream connection pool so a flood of slow requests can't open
    # unbounded sockets to internal services.
    limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=False,
        limits=limits,
    ) as client:
        app.state.http_client = client
        logger.info("gateway_started")
        yield


def create_app() -> FastAPI:
    """Build and configure the gateway ``FastAPI`` application.

    Routes are registered most-specific first so the bare ``GET /{short_code}``
    catch-all (included LAST) cannot shadow ``/auth``, ``/links``, ``/stats``,
    ``/qr``, ``/health``, or the docs routes.
    """
    settings = get_settings()
    configure_logging("gateway", settings.log_level)

    app = FastAPI(
        title="API Gateway",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS matters here specifically: the browser only ever talks to the gateway.
    # Origins are configured explicitly from the environment, never "*".
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )

    @app.middleware("http")
    async def request_context_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """Assign a correlation id, bind it for logging, and add safety headers.

        Honors an inbound ``X-Request-ID`` if present (so a caller can correlate a
        request across the whole platform) or generates one. The chosen id is
        stored on ``request.state`` for the proxy to forward upstream, echoed back
        on the response, and bound into the structlog context for this request.
        """
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        request.state.request_id = request_id
        bind_request_id(request_id)

        # Reject oversized bodies up front (memory-exhaustion guard) when the
        # client declares a Content-Length beyond the cap.
        content_length = request.headers.get("content-length")
        if content_length is not None and content_length.isdigit():
            if int(content_length) > settings.max_body_bytes:
                clear_request_context()
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={"detail": "Request body too large"},
                )

        try:
            response = await call_next(request)
        finally:
            clear_request_context()
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = (
            "max-age=63072000; includeSubDomains"
        )
        return response

    app.add_exception_handler(GatewayDomainError, handle_domain_error)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    @app.get("/health", status_code=status.HTTP_200_OK, tags=["health"])
    async def health() -> JSONResponse:
        """Gateway liveness probe (not proxied to any backend)."""
        return JSONResponse({"status": "ok"})

    # Registration order is load-bearing: specific prefixes first, the bare
    # short-code catch-all LAST so it can never shadow a real route.
    app.include_router(auth_router)
    app.include_router(links_router)
    app.include_router(stats_router)
    app.include_router(qr_router)
    app.include_router(redirect_router)

    logger.info("gateway_configured")
    return app


app = create_app()
