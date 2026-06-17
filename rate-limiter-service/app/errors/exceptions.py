"""Rate limiter domain exceptions and the handlers that render them.

Client-facing responses are always generic; operational detail goes to the logs.
"""

from __future__ import annotations

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class RateLimiterDomainError(Exception):
    """Base class for expected errors mapped to clean HTTP responses."""

    status_code = status.HTTP_400_BAD_REQUEST
    client_message = "Request could not be completed"


class UnauthorizedError(RateLimiterDomainError):
    """Raised when the internal-key check fails."""

    status_code = status.HTTP_401_UNAUTHORIZED
    client_message = "Invalid credentials"


class UnknownActionError(RateLimiterDomainError):
    """Raised when the requested action is not in the allow-list."""

    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    client_message = "Invalid request"


async def domain_exception_handler(
    _request: Request,
    exc: RateLimiterDomainError,
) -> JSONResponse:
    """Render a :class:`RateLimiterDomainError` as a generic JSON response."""
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
    _exc: Exception,
) -> JSONResponse:
    """Catch-all handler so an unexpected error never leaks a stack trace."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )
