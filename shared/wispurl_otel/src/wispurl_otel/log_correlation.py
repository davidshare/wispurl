"""structlog processor that stamps each log line with the active trace and span."""

from __future__ import annotations

from typing import Any

from opentelemetry import trace


def add_trace_context(
    _logger: Any,
    _method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    span_context = trace.get_current_span().get_span_context()
    if span_context.is_valid:
        # The same hex format Tempo and Grafana display, so IDs can be searched as-is.
        event_dict["trace_id"] = format(span_context.trace_id, "032x")
        event_dict["span_id"] = format(span_context.span_id, "016x")
    return event_dict
