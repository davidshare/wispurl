---
id: LOC-7.07
title: "Health checks configured for all downstream dependencies"
category: "7. Reliability and SRE (Local Validation)"
status: done
---

# Health checks configured for all downstream dependencies

## What
Every downstream dependency has a health check, and dependants wait for it to be healthy.

## Current state
Compose healthchecks exist for Postgres (`pg_isready`), Redis (`PING`), RabbitMQ (`diagnostics ping`) and Vault (`status`); services gate on `service_healthy`.

## Subtasks
- [x] Healthchecks on Postgres, Redis, RabbitMQ and Vault
- [x] Dependants use `depends_on: condition: service_healthy`

## Acceptance criteria
- [x] `docker compose ps` shows all dependencies healthy before services start

## Notes
- In-app dependency checks (`/ready`) are tracked in [Health endpoints](../application-foundations/04-health-ready-live-endpoints.md).

## References
- [docker-compose.yml](../../../docker-compose.yml)
