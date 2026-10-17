---
id: LOC-1.07
title: "Correlation/request IDs propagated across all service boundaries (via contextvars)"
category: "1. Application Foundations"
status: done
related:
  - docs/local/app/app-02-service-health-shutdown-logging-and-request-correlation.md
---

# Correlation/request IDs propagated across all service boundaries (via `contextvars`)

## What
A single request ID follows a request through the gateway, every downstream HTTP call and every RabbitMQ message, bound with `contextvars` so every log line carries it.

## Current state
The gateway accepts or generates `X-Request-ID`, forwards it upstream and echoes it. Each service binds it via structlog contextvars; messages carry an `x-request-id` header that consumers bind.

## Subtasks
- [x] Gateway honours inbound `X-Request-ID` or generates a UUID and echoes it on the response
- [x] Gateway proxy forwards the header to upstream services
- [x] Every HTTP service middleware binds the ID into the structlog context
- [x] RabbitMQ envelopes carry `x-request-id` and consumers bind it
- [x] Context is cleared at the end of each request/message

## Acceptance criteria
- [x] One request through the gateway produces log lines in each touched service with the same `request_id`

## References
- [gateway/app/main.py](../../../gateway/app/main.py)
- [gateway/app/proxy.py](../../../gateway/app/proxy.py)
- [shortener-service/shared/messaging.py](../../../shortener-service/shared/messaging.py)
