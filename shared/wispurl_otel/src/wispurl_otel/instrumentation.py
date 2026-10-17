"""OpenTelemetry tracing setup shared by every WispURL service.

Everything that differs between environments (where spans go, sampling, batch
sizes, timeouts, resource attributes) comes from the standard OTEL_* variables.
"""

from __future__ import annotations

import importlib.util
import os
from typing import TYPE_CHECKING

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

if TYPE_CHECKING:
    from fastapi import FastAPI
    from sqlalchemy.ext.asyncio import AsyncEngine

# Probe and scrape endpoints run every few seconds and say nothing about user
# traffic, so they are not traced. Each entry is a regex matched against the URL.
EXCLUDED_URLS = "/health$,/ready$,/live$,/metrics$"

_configured = False


def setup_otel(service_name: str) -> None:
    """Create the tracer provider and instrument outgoing httpx calls.

    Call once per process, before any httpx client is created. Calling it again
    is a no-op.
    """
    global _configured
    if _configured:
        return
    _configured = True
    if os.getenv("OTEL_SDK_DISABLED", "false").lower() == "true":
        return

    # Resource.create also merges OTEL_RESOURCE_ATTRIBUTES (environment, version).
    resource = Resource.create({"service.name": service_name})
    # The sampler comes from OTEL_TRACES_SAMPLER / OTEL_TRACES_SAMPLER_ARG.
    provider = TracerProvider(resource=resource)
    # The exporter reads OTEL_EXPORTER_OTLP_ENDPOINT and _TIMEOUT; the batch
    # processor reads OTEL_BSP_*. Export runs on a background thread, so a slow or
    # missing collector never blocks a request: spans are retried, then dropped.
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)

    # Adds a W3C `traceparent` header to every outgoing httpx request. The
    # receiving service's FastAPI instrumentation reads it and continues the
    # same trace, which is what connects spans across services.
    # The workers don't use httpx, so only instrument it where it's installed.
    if importlib.util.find_spec("httpx") is not None:
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

        HTTPXClientInstrumentor().instrument()


def instrument_fastapi(app: FastAPI) -> None:
    """Create a server span for every incoming request, except probes."""
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    FastAPIInstrumentor.instrument_app(app, excluded_urls=EXCLUDED_URLS)


def instrument_sqlalchemy(engine: AsyncEngine) -> None:
    """Create a span for every SQL statement sent through ``engine``."""
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)


def instrument_redis() -> None:
    """Create a span for every Redis command. Call before creating Redis clients."""
    from opentelemetry.instrumentation.redis import RedisInstrumentor

    RedisInstrumentor().instrument()
