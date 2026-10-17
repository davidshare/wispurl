---
id: LOC-1.06
title: "Structured JSON logging with standardized fields"
category: "1. Application Foundations"
status: done
related:
  - docs/local/app/app-02-service-health-shutdown-logging-and-request-correlation.md
---

# Structured JSON logging with standardized fields

## What
All services emit one JSON object per log line with a consistent field set so logs are machine-searchable in Loki.

## Current state
Each service's `shared/logging_config.py` configures structlog with `JSONRenderer`, ISO timestamps, level, `service`, and context-bound `request_id`.

## Subtasks
- [x] structlog configured with `JSONRenderer` in every service
- [x] Standard fields: timestamp, level, event, service, request_id
- [x] Log level configurable via `LOG_LEVEL`
- [x] Context cleared after each request/message

## Acceptance criteria
- [x] `docker compose logs <service>` shows valid JSON lines with the standard fields

## Notes
- Adding `trace_id`/`span_id` to log lines is tracked in [Distributed tracing](../observability/10-opentelemetry-tracing.md).

## References
- [auth-service/shared/logging_config.py](../../../auth-service/shared/logging_config.py)
