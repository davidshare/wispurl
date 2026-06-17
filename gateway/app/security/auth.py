"""Local JWT verification for protected gateway routes.

This implements the SAME token contract as every backend service: HS256 pinned,
``exp``/``nbf`` enforced, ``token_type == "access"`` required, and ``sub`` parsed
to a UUID. Verification is performed locally with the shared secret and involves no
network call to the Auth service.

DEFENSE IN DEPTH (intentional): the gateway verifies the token here AND each backend
service verifies it again locally. We deliberately do NOT replace backend
verification by having the gateway inject a trusted ``X-User-Id`` header — on the
internal Docker network any peer could spoof such a header, which is a strictly
weaker trust model. The gateway forwards the ``Authorization`` header upstream
unchanged so the backend can independently re-verify and read ``sub`` itself. Do not
"optimize" this duplication away.
"""

from __future__ import annotations

from typing import Annotated, Any
from uuid import UUID

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import GatewaySettings, get_settings
from app.errors.exceptions import UnauthorizedError
from shared.jwt_utils import verify_access_token

# auto_error=False so a missing/garbled Authorization header reaches our own code
# and yields a generic 401, rather than FastAPI's default 403 with a leaky message.
bearer_scheme = HTTPBearer(auto_error=False)


def _extract_bearer_token(credentials: HTTPAuthorizationCredentials | None) -> str:
    """Return the raw bearer token, or raise 401 if absent/not a bearer scheme."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError
    return credentials.credentials


def _parse_user_id(claims: dict[str, Any]) -> UUID:
    """Validate the access-token claims and return the subject as a UUID.

    Rejects any token that is not an access token (e.g. a refresh token) and any
    token whose ``sub`` is missing or not a valid UUID.
    """
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
    settings: Annotated[GatewaySettings, Depends(get_settings)],
) -> UUID:
    """FastAPI dependency that authenticates a request and returns its user id.

    Used as a route dependency on protected proxy routes. Its return value is not
    consumed by the proxy (the Authorization header is forwarded so the backend
    re-verifies), but verification here fails closed with a generic 401 on any
    invalid/expired/missing token before the request is forwarded.
    """
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
