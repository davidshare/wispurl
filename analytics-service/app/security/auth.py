"""Access-token verification for ``GET /stats`` (AUTHZ option (a)).

AUTHZ DECISION: link ownership lives in the Shortener, and analytics has no users
table of its own. We therefore verify only that the caller presents a valid access
token (same HS256 contract as every service) — this proves the caller is logged in,
NOT that they own the short code whose stats they request.

TODO(ownership): true per-link authorization would require the gateway (or this
service) to confirm with the Shortener that the authenticated user owns the
short_code before returning its stats. Until then, stats for a given code are
visible to any authenticated user who knows the code.
"""

from __future__ import annotations

from typing import Annotated, Any
from uuid import UUID

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import AnalyticsSettings, get_settings
from app.errors.exceptions import UnauthorizedError
from shared.jwt_utils import verify_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def _extract_bearer_token(credentials: HTTPAuthorizationCredentials | None) -> str:
    """Return the raw bearer token, or raise 401 if absent/not a bearer scheme."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError
    return credentials.credentials


def _parse_user_id(claims: dict[str, Any]) -> UUID:
    """Validate access-token claims and return the subject as a UUID."""
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
    settings: Annotated[AnalyticsSettings, Depends(get_settings)],
) -> UUID:
    """Authenticate the caller and return their user id (fails closed with 401)."""
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
