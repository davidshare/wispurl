"""Publishing of ``link.expired`` events for deactivated links."""

from __future__ import annotations

from shared.messaging import (
    ROUTING_KEY_LINK_EXPIRED,
    EventPublisher,
    build_envelope,
)


async def publish_link_expired(publisher: EventPublisher, short_code: str) -> None:
    """Publish one ``link.expired`` event for a deactivated short code."""
    envelope = build_envelope(
        event=ROUTING_KEY_LINK_EXPIRED,
        data={"short_code": short_code},
    )
    await publisher.publish(envelope, routing_key=ROUTING_KEY_LINK_EXPIRED)
