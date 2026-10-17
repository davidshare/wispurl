---
id: LOC-1.05
title: "Graceful shutdown handling (SIGTERM) in application code"
category: "1. Application Foundations"
status: partial
related:
  - docs/local/app/app-02-service-health-shutdown-logging-and-request-correlation.md
---

# Graceful shutdown handling (SIGTERM) in application code

## What
On SIGTERM every process stops accepting work, finishes or safely requeues in-flight work, closes connections and exits within the grace period.

## Current state
HTTP services run under gunicorn/uvicorn workers via `exec` (SIGTERM reaches gunicorn) and lifespans close the httpx/Redis clients. The asyncio workers have no signal handling, so a stop kills them mid-message.

## Subtasks
- [x] Entrypoints use `exec` so PID 1 receives signals
- [x] Lifespan handlers close shared clients in gateway, shortener and rate-limiter
- [ ] Add SIGTERM/SIGINT handlers in analytics-consumer, cleanup and notification that stop consuming, finish the current message and close the channel/connection
- [ ] Dispose SQLAlchemy engines on shutdown
- [ ] Set gunicorn `--graceful-timeout` and Compose `stop_grace_period` (later `terminationGracePeriodSeconds`)
- [ ] Test: `docker compose stop` under load causes no 5xx and no lost messages

## Acceptance criteria
- [ ] Each worker logs a clean shutdown event on SIGTERM
- [ ] An in-flight RabbitMQ message is either acked or redelivered — never lost

## References
- [auth-service/entrypoint.sh](../../../auth-service/entrypoint.sh)
- [cleanup-service/app/main.py](../../../cleanup-service/app/main.py)
- [notification-service/app/main.py](../../../notification-service/app/main.py)
