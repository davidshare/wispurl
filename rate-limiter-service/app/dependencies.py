"""Shared FastAPI dependencies for the rate limiter service."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request
from redis.asyncio import Redis

from app.config import RateLimiterSettings, get_settings


def get_redis(request: Request) -> Redis:
    """Return the shared async Redis client opened by the lifespan handler."""
    redis: Redis = request.app.state.redis
    return redis


SettingsDep = Annotated[RateLimiterSettings, Depends(get_settings)]
RedisDep = Annotated[Redis, Depends(get_redis)]
