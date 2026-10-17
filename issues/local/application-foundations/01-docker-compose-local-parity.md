---
id: LOC-1.01
title: "Docker Compose configuration for local development parity"
category: "1. Application Foundations"
status: done
related:
  - docs/local/docker/docker-01-docker-compose-local-stack-baseline.md
---

# Docker Compose configuration for local development parity

## What
One Compose project runs the full WispURL stack locally (data stores, Vault, every service, frontend) so development mirrors the deployed topology.

## Current state
`docker-compose.yml` runs Postgres, pgAdmin, Redis, RabbitMQ, Vault + unseal sidecar, 9 backend processes and the frontend on `wispurl-network`. Observability runs as a separate project (`compose.observability.yaml`) that joins the app network.

## Subtasks
- [x] Define Postgres, Redis, RabbitMQ and Vault with healthchecks
- [x] Define every application service with its build context and the `shared_lib` additional context
- [x] Gate startup with `depends_on: condition: service_healthy` / `service_completed_successfully`
- [x] Bind data-store and admin ports to `127.0.0.1` only
- [x] Persist Postgres and RabbitMQ data in named volumes
- [x] Run observability as a separate Compose project attached via the external app network

## Acceptance criteria
- [x] `docker compose up --build -d` brings every service to running/healthy
- [x] Gateway `/health` answers on `http://localhost:8080/health` and the frontend loads on `:3000`

## References
- [docker-compose.yml](../../../docker-compose.yml)
- [compose.observability.yaml](../../../compose.observability.yaml)
- [README.md](../../../README.md)
