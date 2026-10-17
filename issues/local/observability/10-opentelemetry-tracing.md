---
id: LOC-6.10
title: "Distributed tracing implemented with OpenTelemetry"
category: "6. Observability (Local Stack)"
status: partial
related:
  - docs/local/observability/obs-03-opentelemetry-instrumentation-in-wispurl-services.md
---

# Distributed tracing implemented with OpenTelemetry

## What
Traces follow a request across the gateway, downstream services, the database and RabbitMQ, and are exported via Alloy to Tempo.

## Current state
`shared/wispurl_otel` sets up a TracerProvider + OTLP gRPC exporter, and inbound FastAPI requests are traced in 6 services. Outbound calls aren't instrumented, so traces don't connect across services. **On the current branch all six `main.py` files put `import os` before `from __future__ import annotations` (SyntaxError).**

## Subtasks
- [x] Shared `wispurl_otel` library (TracerProvider, OTLP exporter, resource attributes)
- [x] Inbound FastAPI instrumentation in all 6 HTTP services
- [x] Compose OTel env pointing at `alloy:4317`
- [ ] Fix import order in all six `app/main.py` files
- [ ] Instrument outbound httpx so trace context propagates (gateway → services, shortener → analytics/rate-limiter)
- [ ] Instrument SQLAlchemy and Redis
- [ ] Instrument aio-pika publish/consume and inject/extract context in message headers
- [ ] Call `setup_otel` in analytics-consumer, cleanup and notification workers
- [ ] Exclude `/health` and `/metrics` from tracing
- [ ] Configure sampling and exporter timeout/queue limits
- [ ] Add `trace_id`/`span_id` to structlog output
- [ ] Verify services keep running when Alloy is down
- [ ] Fill in `shared/wispurl_otel/README.md` (usage, env vars) and replace the placeholder `description` in its `pyproject.toml`

## Acceptance criteria
- [ ] One request through the gateway appears as a single trace spanning at least two downstream services
- [ ] A RabbitMQ analytics event shows linked producer/consumer spans
- [ ] Stopping Alloy does not crash any service

## References
- [shared/wispurl_otel/src/wispurl_otel/instrumentation.py](../../../shared/wispurl_otel/src/wispurl_otel/instrumentation.py)
- [docker-compose.yml](../../../docker-compose.yml)
