from __future__ import annotations

import hmac
import secrets
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from uuid import uuid4

from app.config import AuthSettings
from shared.jwt_utils import create_access_token


def mint_access_token(user_id: str, settings: AuthSettings) -> str:
    return create_access_token(
        subject=user_id,
        secret=settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
        ttl=timedelta(minutes=settings.access_token_ttl_minutes),
    )


def generate_refresh_token(settings: AuthSettings) -> str:
    return secrets.token_urlsafe(settings.refresh_token_bytes)


def hash_refresh_token(refresh_token: str, settings: AuthSettings) -> str:
    return hmac.new(
        settings.jwt_secret.encode("utf-8"),
        refresh_token.encode("utf-8"),
        sha256,
    ).hexdigest()


def new_family_id() -> str:
    return str(uuid4())


def refresh_token_expiry(settings: AuthSettings) -> datetime:
    return datetime.now(UTC) + timedelta(days=settings.refresh_token_ttl_days)
