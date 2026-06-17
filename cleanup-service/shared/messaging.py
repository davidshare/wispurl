"""Shared RabbitMQ topology, event envelope, and robust producer/consumer helpers.

Every producer and consumer declares the SAME topology (idempotently, on startup)
from this one module, so no service depends on another service's code:

    exchange "events"            topic, durable
    queue    "analytics.clicks"  durable, bound to "link.clicked"
    queue    "notifications.all" durable, bound to "link.expired", "link.milestone"
    queue    "events.dlq"        durable dead-letter sink for poison/exhausted events

Robustness guarantees provided here:
  * Producers use publisher confirms and persistent (delivery_mode=2) messages.
  * Consumers use manual acks with a prefetch (QoS) cap.
  * Every consumed payload is validated as an :class:`EventEnvelope`; malformed
    messages are dead-lettered immediately (never retried, never trusted).
  * Processing failures are retried up to ``max_attempts`` by republishing the
    message to the tail of its queue with an incremented ``x-attempt`` header, then
    dead-lettered — so a poison message can never loop forever.
  * Connections use ``connect_robust`` and the consume loop is wrapped in an
    exponential-backoff retry, so producers and consumers survive a broker bounce.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import aio_pika
import structlog
from aio_pika import DeliveryMode, ExchangeType, Message
from aio_pika.abc import (
    AbstractExchange,
    AbstractIncomingMessage,
    AbstractQueue,
    AbstractRobustConnection,
)
from pydantic import BaseModel, ConfigDict, ValidationError

logger = structlog.get_logger()

EXCHANGE_NAME = "events"
DLQ_NAME = "events.dlq"

QUEUE_ANALYTICS_CLICKS = "analytics.clicks"
QUEUE_NOTIFICATIONS_ALL = "notifications.all"

ROUTING_KEY_LINK_CLICKED = "link.clicked"
ROUTING_KEY_LINK_EXPIRED = "link.expired"
ROUTING_KEY_LINK_MILESTONE = "link.milestone"


class EventEnvelope(BaseModel):
    """Versioned JSON event passed over the queue, validated on both ends."""

    model_config = ConfigDict(extra="forbid")

    event: str
    version: int = 1
    data: dict[str, Any]
    occurred_at: datetime
    request_id: str | None = None


def build_envelope(
    *,
    event: str,
    data: dict[str, Any],
    request_id: str | None = None,
) -> EventEnvelope:
    """Construct an :class:`EventEnvelope` stamped with the current UTC time."""
    return EventEnvelope(
        event=event,
        version=1,
        data=data,
        occurred_at=datetime.now(UTC),
        request_id=request_id,
    )


@dataclass
class Topology:
    """References to the declared exchange and queues."""

    exchange: AbstractExchange
    queues: dict[str, AbstractQueue]
    dead_letter_queue: AbstractQueue


async def connect(rabbitmq_url: str) -> AbstractRobustConnection:
    """Open a robust (auto-reconnecting) connection to the broker."""
    return await aio_pika.connect_robust(rabbitmq_url)


async def declare_topology(channel: aio_pika.abc.AbstractChannel) -> Topology:
    """Idempotently declare the exchange, queues, bindings, and DLQ."""
    exchange = await channel.declare_exchange(
        EXCHANGE_NAME,
        ExchangeType.TOPIC,
        durable=True,
    )
    dead_letter_queue = await channel.declare_queue(DLQ_NAME, durable=True)

    analytics_queue = await channel.declare_queue(
        QUEUE_ANALYTICS_CLICKS,
        durable=True,
    )
    await analytics_queue.bind(exchange, routing_key=ROUTING_KEY_LINK_CLICKED)

    notifications_queue = await channel.declare_queue(
        QUEUE_NOTIFICATIONS_ALL,
        durable=True,
    )
    await notifications_queue.bind(exchange, routing_key=ROUTING_KEY_LINK_EXPIRED)
    await notifications_queue.bind(exchange, routing_key=ROUTING_KEY_LINK_MILESTONE)

    return Topology(
        exchange=exchange,
        queues={
            QUEUE_ANALYTICS_CLICKS: analytics_queue,
            QUEUE_NOTIFICATIONS_ALL: notifications_queue,
        },
        dead_letter_queue=dead_letter_queue,
    )


class EventPublisher:
    """Publishes durable events to the topic exchange with publisher confirms."""

    def __init__(
        self,
        channel: aio_pika.abc.AbstractChannel,
        exchange: AbstractExchange,
    ) -> None:
        self._channel = channel
        self._exchange = exchange

    async def publish(self, envelope: EventEnvelope, *, routing_key: str) -> None:
        """Publish ``envelope`` under ``routing_key`` (awaits the broker confirm)."""
        message = Message(
            body=envelope.model_dump_json().encode("utf-8"),
            delivery_mode=DeliveryMode.PERSISTENT,
            content_type="application/json",
            headers={"x-attempt": 1, "x-request-id": envelope.request_id or ""},
        )
        await self._exchange.publish(message, routing_key=routing_key)


async def create_publisher(connection: AbstractRobustConnection) -> EventPublisher:
    """Open a confirms-enabled channel, declare topology, and return a publisher."""
    channel = await connection.channel(publisher_confirms=True)
    topology = await declare_topology(channel)
    return EventPublisher(channel, topology.exchange)


def _header_int(message: AbstractIncomingMessage, key: str, default: int) -> int:
    """Read an integer header value defensively (queue input is untrusted)."""
    raw = (message.headers or {}).get(key, default)
    return raw if isinstance(raw, int) else default


def _header_str(message: AbstractIncomingMessage, key: str) -> str | None:
    """Read a string header value defensively."""
    raw = (message.headers or {}).get(key)
    return raw if isinstance(raw, str) and raw else None


async def _dead_letter(
    channel: aio_pika.abc.AbstractChannel,
    message: AbstractIncomingMessage,
) -> None:
    """Route a message body to the dead-letter queue."""
    await channel.default_exchange.publish(
        Message(
            body=message.body,
            delivery_mode=DeliveryMode.PERSISTENT,
            content_type="application/json",
            headers=dict(message.headers or {}),
        ),
        routing_key=DLQ_NAME,
    )


async def _republish_for_retry(
    channel: aio_pika.abc.AbstractChannel,
    message: AbstractIncomingMessage,
    queue_name: str,
    next_attempt: int,
) -> None:
    """Re-enqueue a message to the tail of its queue with a bumped attempt count."""
    headers = dict(message.headers or {})
    headers["x-attempt"] = next_attempt
    await channel.default_exchange.publish(
        Message(
            body=message.body,
            delivery_mode=DeliveryMode.PERSISTENT,
            content_type="application/json",
            headers=headers,
        ),
        routing_key=queue_name,
    )


EventHandler = Callable[[EventEnvelope], Awaitable[None]]


async def _process_message(
    channel: aio_pika.abc.AbstractChannel,
    queue_name: str,
    message: AbstractIncomingMessage,
    handler: EventHandler,
    max_attempts: int,
) -> None:
    """Validate, dispatch, and ack/retry/dead-letter a single message."""
    from shared.logging_config import bind_request_id, clear_request_context

    bind_request_id(_header_str(message, "x-request-id"))
    try:
        try:
            envelope = EventEnvelope.model_validate_json(message.body)
        except ValidationError as exc:
            logger.warning("event_malformed_dead_lettered", error=str(exc))
            await _dead_letter(channel, message)
            await message.ack()
            return

        attempt = _header_int(message, "x-attempt", 1)
        try:
            await handler(envelope)
            await message.ack()
        except Exception as exc:  # noqa: BLE001 - bounded retry, then dead-letter
            if attempt >= max_attempts:
                logger.error(
                    "event_dropped_to_dlq",
                    event_type=envelope.event,
                    attempt=attempt,
                    error=str(exc),
                )
                await _dead_letter(channel, message)
                await message.ack()
            else:
                logger.warning(
                    "event_retry",
                    event_type=envelope.event,
                    attempt=attempt,
                    error=str(exc),
                )
                await _republish_for_retry(channel, message, queue_name, attempt + 1)
                await message.ack()
    finally:
        clear_request_context()


async def run_consumer(
    *,
    connection: AbstractRobustConnection,
    queue_name: str,
    handler: EventHandler,
    prefetch: int = 10,
    max_attempts: int = 5,
) -> None:
    """Consume ``queue_name`` until cancelled, dispatching each event to ``handler``."""
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=prefetch)
    topology = await declare_topology(channel)
    queue = topology.queues[queue_name]

    async with queue.iterator() as iterator:
        async for message in iterator:
            await _process_message(
                channel,
                queue_name,
                message,
                handler,
                max_attempts,
            )


async def run_consumer_forever(
    *,
    rabbitmq_url: str,
    queue_name: str,
    handler: EventHandler,
    prefetch: int = 10,
    max_attempts: int = 5,
    max_backoff_seconds: float = 30.0,
) -> None:
    """Run :func:`run_consumer`, reconnecting with exponential backoff on failure."""
    backoff = 1.0
    while True:
        try:
            connection = await connect(rabbitmq_url)
            async with connection:
                logger.info("consumer_connected", queue=queue_name)
                backoff = 1.0
                await run_consumer(
                    connection=connection,
                    queue_name=queue_name,
                    handler=handler,
                    prefetch=prefetch,
                    max_attempts=max_attempts,
                )
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001 - survive any broker disruption
            logger.warning(
                "consumer_reconnecting",
                queue=queue_name,
                error=str(exc),
                backoff=backoff,
            )
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, max_backoff_seconds)
