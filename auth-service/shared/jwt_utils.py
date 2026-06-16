from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import jwt


def create_access_token(
    *,
    subject: str,
    secret: str,
    algorithm: str,
    ttl: timedelta,
    issued_at: datetime | None = None,
) -> str:
    now = issued_at or datetime.now(UTC)
    claims: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "nbf": now,
        "exp": now + ttl,
        "jti": str(uuid4()),
        "token_type": "access",
    }
    return jwt.encode(claims, secret, algorithm=algorithm)


def verify_access_token(*, token: str, secret: str, algorithm: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        secret,
        algorithms=[algorithm],
        options={"require": ["sub", "iat", "nbf", "exp", "jti", "token_type"]},
    )
