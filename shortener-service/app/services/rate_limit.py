from __future__ import annotations

from uuid import UUID

from app.config import ShortenerSettings


async def check_rate_limit(
    *,
    user_id: UUID,
    settings: ShortenerSettings,
) -> bool:
    """TODO: replace with httpx POST to RATE_LIMITER_URL/check (with a timeout).

    Fail policy: this stub deliberately fails OPEN so link creation is not blocked
    by a dependency that does not exist yet. The real limiter should instead fail
    CLOSED on timeout/error (return False -> 429): a limiter that silently fails
    open under load defeats its own purpose. Make that the deliberate choice when
    wiring the httpx call, and set an explicit short timeout so a slow limiter
    cannot stall link creation.
    """

    _ = (user_id, settings)
    return True
