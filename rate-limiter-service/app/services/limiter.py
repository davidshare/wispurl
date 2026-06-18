"""The rate-limiting algorithm: a per-user, per-action FIXED WINDOW counter.

For each (action, user, window) we keep a Redis integer counter at
``rl:{action}:{user_id}:{window_start_epoch}``. Each check atomically increments the
counter and, on the first increment of a fresh window, sets its TTL to the window
length — done in a single Lua script so a counter can never be left without a TTL
(which would leak keys forever). A request is allowed while the post-increment count
is within the configured limit.

ALTERNATIVE (not shipped) — SLIDING WINDOW via a sorted set, for smoother limiting
without fixed-window edge bursts:
    ZADD   rl:{action}:{user_id}  now  <unique-member>
    ZREMRANGEBYSCORE rl:...  -inf  (now - window)   # drop entries older than window
    ZCARD  rl:{action}:{user_id}                    # current count in the window
    EXPIRE rl:...  window                            # keep the key bounded
The fixed-window version below is shipped for its O(1) cost and simplicity.
"""

from __future__ import annotations

from collections.abc import Awaitable
from datetime import UTC, datetime, timedelta
from typing import cast

import structlog
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.config import RateLimiterSettings
from app.errors.exceptions import LimiterUnavailableError
from app.schemas.check import CheckResponse

logger = structlog.get_logger()

# Atomic INCR + first-write EXPIRE, returning the new count and the key's TTL.
# KEYS[1] = counter key, ARGV[1] = window length in seconds.
_INCR_AND_EXPIRE = """
local current = redis.call('INCR', KEYS[1])
if current == 1 then
  redis.call('EXPIRE', KEYS[1], ARGV[1])
end
local ttl = redis.call('TTL', KEYS[1])
return {current, ttl}
"""


class RateLimiter:
    """Applies fixed-window limits using atomic Redis counters."""

    def __init__(self, redis: Redis, settings: RateLimiterSettings) -> None:
        self._redis = redis
        self._settings = settings

    async def check(self, *, user_id: str, action: str, limit: int) -> CheckResponse:
        """Count one attempt for (user, action) and report whether it is allowed.

        Args:
            user_id: The (already UUID-validated) caller identity.
            action: The (already allow-list-validated) action being attempted.
            limit: The per-window limit configured for ``action``.

        Returns:
            A :class:`CheckResponse` with ``allowed``, ``remaining``, ``reset_at``,
            and the ``limit`` in effect.
        """
        window = self._settings.window_seconds
        now = datetime.now(UTC)
        window_start = int(now.timestamp()) // window * window
        key = f"rl:{action}:{user_id}:{window_start}"

        # redis-py types eval() for the sync client; cast the call to its real async
        # shape. The Lua script returns [count, ttl] as RESP integers. A Redis
        # outage/timeout surfaces as a deliberate 503 (LimiterUnavailableError)
        # rather than an opaque 500, leaving the fail policy to the caller.
        try:
            eval_result = cast(
                "Awaitable[list[int]]",
                self._redis.eval(_INCR_AND_EXPIRE, 1, key, str(window)),
            )
            count, ttl = await eval_result
        except RedisError as exc:
            logger.warning("rate_limiter_redis_unavailable", error=str(exc))
            raise LimiterUnavailableError from exc

        # Fall back to the full window if the TTL read raced to -1/-2 (key just set).
        seconds_remaining = ttl if ttl and ttl > 0 else window
        return CheckResponse(
            allowed=count <= limit,
            remaining=max(0, limit - count),
            reset_at=now + timedelta(seconds=seconds_remaining),
            limit=limit,
        )
