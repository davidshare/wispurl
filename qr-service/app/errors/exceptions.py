"""QR domain exceptions and the handlers that render them.

Client-facing responses are always generic; operational detail goes to the logs.
"""

from __future__ import annotations

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class QrDomainError(Exception):
    """Base class for expected QR errors mapped to clean HTTP responses."""

    status_code = status.HTTP_400_BAD_REQUEST
    client_message = "Request could not be completed"


class InvalidShortCodeError(QrDomainError):
    """Raised when the path short code is malformed."""

    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    client_message = "Invalid request"


async def domain_exception_handler(
    _request: Request,
    exc: QrDomainError,
) -> JSONResponse:
    """Render a :class:`QrDomainError` as a generic JSON response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.client_message},
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
