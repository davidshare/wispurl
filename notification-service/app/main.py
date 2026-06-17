"""Notification consumer entrypoint (queue-driven).

Run with ``python -m app.main``. Consumes ``notifications.all`` and dispatches each
event to its handler. Acks are manual and happen only after the handler succeeds;
failures are retried then dead-lettered (handled by :func:`shared.messaging`).
"""

from __future__ import annotations

import asyncio

import structlog

from app.config import get_settings
from app.consumer import build_handler
from shared import messaging
from shared.logging_config import configure_logging
from shared.messaging import QUEUE_NOTIFICATIONS_ALL

logger = structlog.get_logger()

_PREFETCH = 10
_MAX_ATTEMPTS = 5


async def main() -> None:
    """Consume notification events forever (reconnecting with backoff)."""
    settings = get_settings()
    configure_logging("notification-service", settings.log_level)
    logger.info("notification_started", channel=settings.notify_channel)

    await messaging.run_consumer_forever(
        rabbitmq_url=settings.rabbitmq_url,
        queue_name=QUEUE_NOTIFICATIONS_ALL,
        handler=build_handler(settings),
        prefetch=_PREFETCH,
        max_attempts=_MAX_ATTEMPTS,
    )


if __name__ == "__main__":
    asyncio.run(main())
