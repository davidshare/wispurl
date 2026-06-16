from __future__ import annotations

from uuid import UUID

from app.config import ShortenerSettings


async def check_rate_limit(
    *,
    user_id: UUID,
    settings: ShortenerSettings,
) -> bool:
    """TODO: replace with httpx POST to RATE_LIMITER_URL/check.

    This deliberately fails open while the dedicated Rate Limiter service does not
    exist, so link creation is not blocked by an unavailable future dependency.
    """

    _ = (user_id, settings)
    return True
