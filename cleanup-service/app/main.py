"""Cleanup loop entrypoint (schedule-driven).

Runs the expiry sweep, publishes a ``link.expired`` event per deactivated link, then
sleeps ``CLEANUP_INTERVAL_SECONDS`` and repeats.

NOTE: in the DevOps phase (Prompt 10) this becomes a Kubernetes CronJob — a single
sweep per scheduled invocation with NO long-running loop. The sleep loop here exists
only so the same logic runs as a plain Compose container in the local stack.
"""

from __future__ import annotations

import asyncio

import structlog

from app.config import get_settings
from app.publisher import publish_link_expired
from app.service import sweep_expired_links
from shared import messaging
from shared.logging_config import configure_logging

logger = structlog.get_logger()


async def run_once(publisher: messaging.EventPublisher, batch_size: int) -> None:
    """Run one sweep and publish a ``link.expired`` event per deactivated link.

    Links are deactivated first, then events are published. A publish failure means
    an expiry notification is missed (at-most-once) — acceptable, and the link stays
    correctly deactivated, so the next sweep will not re-process it.
    """
    short_codes = await sweep_expired_links(batch_size)
    if not short_codes:
        logger.info("cleanup_sweep_empty")
        return
    logger.info("cleanup_sweep_deactivated", count=len(short_codes))
    for short_code in short_codes:
        try:
            await publish_link_expired(publisher, short_code)
        except Exception as exc:  # noqa: BLE001 - missed notification is acceptable
            logger.warning(
                "link_expired_publish_failed",
                short_code=short_code,
                error=str(exc),
            )


async def main() -> None:
    """Connect to the broker and run the sweep loop forever (with backoff)."""
    settings = get_settings()
    configure_logging("cleanup-service", settings.log_level)

    backoff = 1.0
    while True:
        try:
            connection = await messaging.connect(settings.rabbitmq_url)
            async with connection:
                publisher = await messaging.create_publisher(connection)
                logger.info(
                    "cleanup_started",
                    interval=settings.cleanup_interval_seconds,
                )
                backoff = 1.0
                while True:
                    await run_once(publisher, settings.batch_size)
                    await asyncio.sleep(settings.cleanup_interval_seconds)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001 - survive broker/DB disruptions
            logger.warning("cleanup_reconnecting", error=str(exc), backoff=backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 30.0)


if __name__ == "__main__":
    asyncio.run(main())
