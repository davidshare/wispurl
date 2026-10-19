---
id: LOC-1.04
title: "Health endpoints: /health, /ready, and /live"
category: "1. Application Foundations"
status: partial
related:
  - docs/local/app/app-02-service-health-shutdown-logging-and-request-correlation.md
---

# Health endpoints: `/health`, `/ready`, and `/live`

## What
Separate liveness (process is alive), readiness (dependencies reachable, can take traffic) and a summary health endpoint, so Compose and Kubernetes can restart or route traffic correctly.

## Current state
All 6 HTTP services expose a static `/health`. There is no `/live` or `/ready`, nothing checks dependencies, and the worker healthchecks only test that `/proc/1/status` exists (always true).

## Subtasks
- [x] `/health` on gateway, auth, shortener, analytics, qr and rate-limiter
- [ ] Add `/live` that returns 200 without touching dependencies
- [ ] Add `/ready` that checks each dependency with a short timeout (Postgres `SELECT 1`, Redis `PING`, RabbitMQ connection, gateway upstreams) and returns 503 on failure
- [x] Give workers (analytics-consumer, cleanup, notification) a real liveness signal (heartbeat file or tiny HTTP server): each worker serves `/metrics` on port 8000 and the Compose healthcheck calls it
- [ ] Make the worker liveness signal prove the main loop is progressing (the metrics thread keeps answering even if the consumer loop hangs), for example by checking a heartbeat timestamp
- [ ] Point Compose healthchecks at `/ready` (the no-op worker checks are replaced)
- [ ] Exclude probe endpoints from request metrics and tracing

## Acceptance criteria
- [ ] Stopping Postgres makes auth `/ready` return 503 while `/live` stays 200, and readiness recovers without a restart
- [ ] A hung worker is reported unhealthy by Compose

## References
- [gateway/app/main.py](../../../gateway/app/main.py)
- [auth-service/app/main.py](../../../auth-service/app/main.py)
- [docker-compose.yml](../../../docker-compose.yml)
