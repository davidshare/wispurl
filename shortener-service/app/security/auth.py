from __future__ import annotations

from typing import Annotated, Any
from uuid import UUID

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import ShortenerSettings, get_settings
from app.errors.exceptions import UnauthorizedError
from shared.jwt_utils import verify_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def _extract_bearer_token(
    credentials: HTTPAuthorizationCredentials | None,
) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError
    return credentials.credentials


def _parse_user_id(claims: dict[str, Any]) -> UUID:
    if claims.get("token_type") != "access":
        raise UnauthorizedError
    subject = claims.get("sub")
    if not isinstance(subject, str):
        raise UnauthorizedError
    try:
        return UUID(subject)
    except ValueError as exc:
        raise UnauthorizedError from exc


async def get_current_user_id(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
    settings: Annotated[ShortenerSettings, Depends(get_settings)],
) -> UUID:
    token = _extract_bearer_token(credentials)
    try:
        claims = verify_access_token(
            token=token,
            secret=settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
        )
    except jwt.PyJWTError as exc:
        raise UnauthorizedError from exc
    return _parse_user_id(claims)
