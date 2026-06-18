"""Gateway domain exceptions and the handlers that render them.

Every error returned to a client is generic: clients never see upstream internals,
stack traces, or the reason a token failed. Operational detail belongs in the logs,
not the HTTP body.
"""

from __future__ import annotations

import structlog
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = structlog.get_logger()


class GatewayDomainError(Exception):
    """Base class for expected gateway errors mapped to clean HTTP responses."""

    status_code = status.HTTP_400_BAD_REQUEST
    client_message = "Request could not be completed"


class UnauthorizedError(GatewayDomainError):
    """Raised when access-token verification fails on a protected route."""

    status_code = status.HTTP_401_UNAUTHORIZED
    client_message = "Invalid credentials"


class NotFoundError(GatewayDomainError):
    """Raised when the catch-all rejects a malformed or reserved short code."""

    status_code = status.HTTP_404_NOT_FOUND
    client_message = "Not found"


class UpstreamUnavailableError(GatewayDomainError):
    """Raised when an upstream service cannot be reached (refused/connect error)."""

    status_code = status.HTTP_502_BAD_GATEWAY
    client_message = "Upstream service unavailable"


class UpstreamTimeoutError(GatewayDomainError):
    """Raised when an upstream service does not respond within the timeout."""

    status_code = status.HTTP_504_GATEWAY_TIMEOUT
    client_message = "Upstream service timed out"


async def domain_exception_handler(
    _request: Request,
    exc: GatewayDomainError,
) -> JSONResponse:
    """Render a :class:`GatewayDomainError` as a generic JSON response.

    Adds a ``WWW-Authenticate`` header on 401 responses so clients know to present
    a bearer token, without disclosing why verification failed.
    """
    headers = None
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        headers = {"WWW-Authenticate": "Bearer"}
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.client_message},
        headers=headers,
    )


async def validation_exception_handler(
    _request: Request,
    _exc: RequestValidationError,
) -> JSONResponse:
    """Render request-validation failures as a generic 422 (no field echoes)."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": "Invalid request"},
    )


async def unhandled_exception_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    """Catch-all handler so an unexpected error never leaks a stack trace."""
    logger.error("unhandled_exception", error=str(exc), exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )
