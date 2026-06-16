from __future__ import annotations

from dataclasses import dataclass

import structlog

from app.config import ShortenerSettings

logger = structlog.get_logger()


@dataclass(frozen=True)
class ClickMetadata:
    ip_address: str | None
    referrer: str | None
    user_agent: str | None


async def log_click(
    *,
    short_code: str,
    metadata: ClickMetadata,
    settings: ShortenerSettings,
) -> None:
    """TODO: replace with fire-and-forget httpx/event call to Analytics.

    Analytics is fail-open by design; redirect latency and success must not depend
    on click logging.
    """

    _ = settings
    logger.info(
        "click_logged_stub",
        short_code=short_code,
        ip_address=metadata.ip_address,
        referrer=metadata.referrer,
        user_agent=metadata.user_agent,
    )
