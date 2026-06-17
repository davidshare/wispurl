"""Queue-driven click consumer (a second process on the analytics image).

Run with ``python -m app.worker``. It consumes ``analytics.clicks``, writes each
click via the SAME :class:`AnalyticsService` method the HTTP ``/events`` handler
uses (no duplicated write logic), and publishes a ``link.milestone`` event whenever a
click pushes a short_code's total across a configured threshold.

Acks are manual and happen only after a successful DB insert (handled by
:func:`shared.messaging.run_consumer`); a failed insert is retried and then
dead-lettered. ``prefetch=1`` keeps ingestion single-flight so milestone crossings
are detected exactly once.
"""

from __future__ import annotations

import asyncio

import structlog

from app.config import get_settings
from app.database import SessionLocal
from app.schemas.event import RecordClickRequest
from app.services.analytics_service import AnalyticsService
from shared import messaging
from shared.logging_config import configure_logging
from shared.messaging import (
    QUEUE_ANALYTICS_CLICKS,
    ROUTING_KEY_LINK_MILESTONE,
    EventEnvelope,
    build_envelope,
)

logger = structlog.get_logger()

# Single-flight ingestion so milestone crossings are exact; bounded retries.
_PREFETCH = 1
_MAX_ATTEMPTS = 5


async def main() -> None:
    """Connect, then consume click events forever (reconnecting with backoff)."""
    settings = get_settings()
    configure_logging("analytics-consumer", settings.log_level)
    milestones = settings.milestone_values

    # A dedicated publisher connection (separate from the consumer's) for emitting
    # milestone events. connect_robust keeps it alive across broker bounces.
    publisher_connection = await messaging.connect(settings.rabbitmq_url)
    publisher = await messaging.create_publisher(publisher_connection)

    async def handle(envelope: EventEnvelope) -> None:
        payload = RecordClickRequest(
            **envelope.data,
            clicked_at=envelope.occurred_at,
        )
        async with SessionLocal() as session:
            service = AnalyticsService(session, settings)
            result = await service.ingest_click(payload, milestones=milestones)

        for threshold in result.crossed_milestones:
            logger.info(
                "milestone_crossed",
                short_code=payload.short_code,
                threshold=threshold,
                total=result.total,
            )
            milestone_event = build_envelope(
                event=ROUTING_KEY_LINK_MILESTONE,
                data={"short_code": payload.short_code, "total": result.total},
                request_id=envelope.request_id,
            )
            await publisher.publish(
                milestone_event,
                routing_key=ROUTING_KEY_LINK_MILESTONE,
            )

    try:
        await messaging.run_consumer_forever(
            rabbitmq_url=settings.rabbitmq_url,
            queue_name=QUEUE_ANALYTICS_CLICKS,
            handler=handle,
            prefetch=_PREFETCH,
            max_attempts=_MAX_ATTEMPTS,
        )
    finally:
        await publisher_connection.close()


if __name__ == "__main__":
    asyncio.run(main())
