from __future__ import annotations

import structlog
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.responses import Response

logger = structlog.get_logger()


class AuthDomainError(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    client_message = "Request could not be completed"


class DuplicateUserError(AuthDomainError):
    status_code = status.HTTP_409_CONFLICT
    client_message = "Request could not be completed"


class InvalidCredentialsError(AuthDomainError):
    status_code = status.HTTP_401_UNAUTHORIZED
    client_message = "Invalid credentials"


class InvalidRefreshTokenError(AuthDomainError):
    status_code = status.HTTP_401_UNAUTHORIZED
    client_message = "Invalid credentials"


class InactiveUserError(AuthDomainError):
    status_code = status.HTTP_401_UNAUTHORIZED
    client_message = "Invalid credentials"


class WeakPasswordError(AuthDomainError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    client_message = "Password does not meet policy"


class TooManyRequestsError(AuthDomainError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    client_message = "Too many requests"


async def domain_exception_handler(
    _request: Request,
    exc: AuthDomainError,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.client_message},
        headers={"WWW-Authenticate": "Bearer"}
        if exc.status_code == status.HTTP_401_UNAUTHORIZED
        else None,
    )


async def validation_exception_handler(
    _request: Request,
    _exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": "Invalid request"},
    )


async def unhandled_exception_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.error("unhandled_exception", error=str(exc), exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


def empty_response() -> Response:
    return Response(status_code=status.HTTP_204_NO_CONTENT)
