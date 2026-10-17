"""Carry trace context through RabbitMQ message headers.

HTTP calls get this from the httpx instrumentation. Messages need it done by
hand: the producer writes `traceparent` into the message headers, and the
consumer reads it back so its span joins the producer's trace.
"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from typing import Any

from opentelemetry import propagate
from opentelemetry.context import Context
from opentelemetry.propagators.textmap import Getter


class _HeaderGetter(Getter[Mapping[str, Any]]):
    """Read AMQP header values, which may arrive as bytes, as strings."""

    def get(self, carrier: Mapping[str, Any], key: str) -> list[str] | None:
        value = carrier.get(key)
        if value is None:
            return None
        if isinstance(value, bytes):
            value = value.decode("utf-8", errors="replace")
        return [str(value)]

    def keys(self, carrier: Mapping[str, Any]) -> list[str]:
        return list(carrier.keys())


_getter = _HeaderGetter()


def inject_trace_context(headers: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
    """Add the current trace context (traceparent, tracestate) to ``headers``."""
    carrier: dict[str, str] = {}
    propagate.inject(carrier)
    headers.update(carrier)
    return headers


def extract_trace_context(headers: Mapping[str, Any] | None) -> Context:
    """Return the trace context stored in message headers (empty if absent)."""
    return propagate.extract(headers or {}, getter=_getter)
