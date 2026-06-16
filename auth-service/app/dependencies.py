from __future__ import annotations

import asyncio
from collections import defaultdict, deque
from collections.abc import AsyncIterator
from time import monotonic
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import AuthSettings, get_settings
from app.database import get_session
from app.errors.exceptions import TooManyRequestsError

SettingsDep = Annotated[AuthSettings, Depends(get_settings)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]

_rate_limit_lock = asyncio.Lock()
_rate_limit_buckets: dict[str, deque[float]] = defaultdict(deque)


async def local_abuse_guard(
    request: Request,
    settings: SettingsDep,
) -> None:
    """Conservative local hook until the dedicated Rate Limiter service exists."""

    client_host = request.client.host if request.client else "unknown"
    route = request.scope.get("path", "unknown")
    bucket_key = f"{client_host}:{route}"
    now = monotonic()
    window_start = now - settings.local_rate_limit_window_seconds

    async with _rate_limit_lock:
        bucket = _rate_limit_buckets[bucket_key]
        while bucket and bucket[0] < window_start:
            bucket.popleft()
        if len(bucket) >= settings.local_rate_limit_max_requests:
            raise TooManyRequestsError
        bucket.append(now)


async def session_dependency() -> AsyncIterator[AsyncSession]:
    async for session in get_session():
        yield session
