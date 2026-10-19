"""Dispatch consumed events to the matching handler."""

from __future__ import annotations

import structlog
from wispurl_metrics.business import NOTIFICATIONS

from app.config import NotificationSettings
from app.handlers import handle_link_expired, handle_link_milestone
from shared.messaging import (
    ROUTING_KEY_LINK_EXPIRED,
    ROUTING_KEY_LINK_MILESTONE,
    EventEnvelope,
    EventHandler,
)

logger = structlog.get_logger()


def build_handler(settings: NotificationSettings) -> EventHandler:
    """Return an event handler that routes each event to its type-specific handler.

    An unrecognized event type is logged and acked (not dead-lettered): it is not a
    poison message, just one this service does not act on.
    """

    async def handle(envelope: EventEnvelope) -> None:
        if envelope.event == ROUTING_KEY_LINK_EXPIRED:
            kind, handler = "link_expired", handle_link_expired
        elif envelope.event == ROUTING_KEY_LINK_MILESTONE:
            kind, handler = "milestone", handle_link_milestone
        else:
            logger.warning("unknown_event_ignored", event_type=envelope.event)
            NOTIFICATIONS.labels(
                type="unknown",
                channel=settings.notify_channel,
                result="ignored",
            ).inc()
            return
        try:
            await handler(settings, envelope)
        except Exception:
            NOTIFICATIONS.labels(
                type=kind,
                channel=settings.notify_channel,
                result="failed",
            ).inc()
            raise
        NOTIFICATIONS.labels(
            type=kind,
            channel=settings.notify_channel,
            result="sent",
        ).inc()

    return handle
