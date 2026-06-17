"""One handler per event type, plus the channel that delivers the notification.

DEFAULT channel is a structured stdout log. The SMTP/Mailtrap path is a clearly
marked optional stub: wiring a real async SMTP client (e.g. aiosmtplib against
Mailtrap) goes in :func:`_deliver` under the ``smtp`` branch. It is intentionally
not implemented so the service carries no mail dependency by default.
"""

from __future__ import annotations

import structlog

from app.config import NotificationSettings
from shared.messaging import EventEnvelope

logger = structlog.get_logger()


async def _deliver(
    settings: NotificationSettings,
    *,
    kind: str,
    message: str,
) -> None:
    """Deliver one notification via the configured channel."""
    if settings.notify_channel == "smtp":
        # OPTIONAL: send via SMTP/Mailtrap here using settings.smtp_* . Left as a
        # marked stub so no mail dependency is required by default.
        logger.info(
            "notification_smtp_stub",
            kind=kind,
            message=message,
            smtp_host=settings.smtp_host,
        )
        return
    logger.info("notification_sent", kind=kind, message=message)


async def handle_link_expired(
    settings: NotificationSettings,
    envelope: EventEnvelope,
) -> None:
    """Notify that a link was deactivated due to expiry."""
    short_code = envelope.data.get("short_code")
    await _deliver(
        settings,
        kind="link.expired",
        message=f"Short link '{short_code}' has expired and was deactivated.",
    )


async def handle_link_milestone(
    settings: NotificationSettings,
    envelope: EventEnvelope,
) -> None:
    """Notify that a link crossed a click milestone."""
    short_code = envelope.data.get("short_code")
    total = envelope.data.get("total")
    await _deliver(
        settings,
        kind="link.milestone",
        message=f"Short link '{short_code}' reached {total} clicks.",
    )
