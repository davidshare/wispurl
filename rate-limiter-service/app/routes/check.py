"""Internal rate-limit check endpoint (``POST /check``).

Gated by the internal shared key and never exposed through the gateway. Validates
the action against the configured allow-list (the ``user_id`` is already validated
as a UUID by the request schema) and returns the limit decision.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.dependencies import RedisDep, SettingsDep
from app.errors.exceptions import UnknownActionError
from app.schemas.check import CheckRequest, CheckResponse
from app.security.internal import require_internal_key
from app.services.limiter import RateLimiter

router = APIRouter(tags=["check"])


@router.post(
    "/v1/check",
    response_model=CheckResponse,
    dependencies=[Depends(require_internal_key)],
)
async def check(
    payload: CheckRequest,
    redis: RedisDep,
    settings: SettingsDep,
) -> CheckResponse:
    """Count one attempt and report whether the caller is within their limit.

    Rejects an action that is not in the configured allow-list with 422, which also
    prevents arbitrary action strings from creating unbounded Redis keys.
    """
    limit = settings.action_limits.get(payload.action)
    if limit is None:
        raise UnknownActionError
    limiter = RateLimiter(redis, settings)
    return await limiter.check(
        user_id=str(payload.user_id),
        action=payload.action,
        limit=limit,
    )
