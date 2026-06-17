from __future__ import annotations

from typing import Any

import jwt


def verify_access_token(*, token: str, secret: str, algorithm: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        secret,
        algorithms=[algorithm],
        options={"require": ["sub", "iat", "nbf", "exp", "jti", "token_type"]},
    )
