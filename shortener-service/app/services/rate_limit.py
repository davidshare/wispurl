from __future__ import annotations

from uuid import UUID

import httpx
import structlog

from app.config import ShortenerSettings

logger = structlog.get_logger()

# The only action this service asks the limiter about. Must match an allow-listed
# action in the Rate Limiter service.
_ACTION_CREATE_LINK = "create_link"


async def check_rate_limit(
    *,
    client: httpx.AsyncClient,
    user_id: UUID,
    settings: ShortenerSettings,
) -> bool:
    """Ask the Rate Limiter whether ``user_id`` may create another link.

    Posts to ``RATE_LIMITER_URL/check`` with the internal shared key and a short
    timeout. Returns ``True`` when the user is within their limit.

    FAIL MODE (configurable via ``RATE_LIMITER_FAIL_OPEN``, default fail-OPEN): if
    the limiter is unreachable, slow, or errors, we DEFAULT TO ALLOWING the create
    and log a warning, so a limiter outage cannot take down link creation. Set
    fail-open to false to fail CLOSED instead — the right choice when preventing
    abuse matters more than availability.
    """
    url = f"{str(settings.rate_limiter_url).rstrip('/')}/v1/check"
    try:
        response = await client.post(
            url,
            json={"user_id": str(user_id), "action": _ACTION_CREATE_LINK},
            headers={"X-Internal-Key": settings.internal_api_key},
            timeout=settings.rate_limiter_request_timeout,
        )
        response.raise_for_status()
        allowed = bool(response.json()["allowed"])
    except Exception as exc:
        logger.warning(
            "rate_limit_check_failed",
            error=str(exc),
            user_id=str(user_id),
            fail_open=settings.rate_limiter_fail_open,
        )
        return settings.rate_limiter_fail_open
    return allowed
