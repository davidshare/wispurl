from __future__ import annotations

from dataclasses import dataclass

import httpx
import structlog

from app.config import ShortenerSettings

logger = structlog.get_logger()


@dataclass(frozen=True)
class ClickMetadata:
    """Request metadata captured at redirect time for analytics."""

    ip_address: str | None
    referrer: str | None
    user_agent: str | None


async def log_click(
    *,
    client: httpx.AsyncClient,
    short_code: str,
    metadata: ClickMetadata,
    settings: ShortenerSettings,
) -> None:
    """Report one click to the Analytics service (fire-and-forget, fail-open).

    Posts to ``ANALYTICS_SERVICE_URL/events`` with the internal shared key. This is
    invoked from a FastAPI ``BackgroundTask`` AFTER the 307 has been sent, and the
    caller wraps it so any exception is swallowed — analytics is never on the
    redirect's critical path. The shared client's timeout bounds how long this can
    run. A failure here means a lost click metric, never a failed redirect.

    NOTE: Prompt 8 replaces this synchronous HTTP call with publishing an event to
    RabbitMQ that the Analytics service consumes, fully decoupling the two.
    """
    url = f"{str(settings.analytics_service_url).rstrip('/')}/events"
    payload = {
        "short_code": short_code,
        "ip_address": metadata.ip_address,
        "referrer": metadata.referrer,
        "user_agent": metadata.user_agent,
    }
    response = await client.post(
        url,
        json=payload,
        headers={"X-Internal-Key": settings.internal_api_key},
    )
    response.raise_for_status()
    logger.info("click_logged", short_code=short_code)
