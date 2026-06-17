"""Dispatch consumed events to the matching handler."""

from __future__ import annotations

import structlog

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
            await handle_link_expired(settings, envelope)
        elif envelope.event == ROUTING_KEY_LINK_MILESTONE:
            await handle_link_milestone(settings, envelope)
        else:
            logger.warning("unknown_event_ignored", event_type=envelope.event)

    return handle
