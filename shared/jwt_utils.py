from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from shared.config import ServiceSettings


_settings = ServiceSettings()


def create_access_token(sub: str, ttl: timedelta | None = None) -> str:
    expires_at = datetime.now(UTC) + (
        ttl or timedelta(minutes=_settings.access_token_ttl_minutes)
    )
    claims = {
        "sub": sub,
        "exp": expires_at,
        "iat": datetime.now(UTC),
    }

    return jwt.encode(
        claims,
        _settings.jwt_secret,
        algorithm=_settings.jwt_algorithm,
    )


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        _settings.jwt_secret,
        algorithms=[_settings.jwt_algorithm],
    )


def verify_token(token: str) -> dict[str, Any]:
    return decode_token(token)
