"""Analytics domain exceptions and the handlers that render them.

Client-facing responses are always generic; operational detail goes to the logs.
"""

from __future__ import annotations

import structlog
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = structlog.get_logger()


class AnalyticsDomainError(Exception):
    """Base class for expected analytics errors mapped to clean HTTP responses."""

    status_code = status.HTTP_400_BAD_REQUEST
    client_message = "Request could not be completed"


class UnauthorizedError(AnalyticsDomainError):
    """Raised when internal-key or access-token verification fails."""

    status_code = status.HTTP_401_UNAUTHORIZED
    client_message = "Invalid credentials"


async def domain_exception_handler(
    _request: Request,
    exc: AnalyticsDomainError,
) -> JSONResponse:
    """Render an :class:`AnalyticsDomainError` as a generic JSON response."""
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
