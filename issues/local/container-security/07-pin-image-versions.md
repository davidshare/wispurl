---
id: LOC-5.07
title: "Image versions pinned explicitly; no latest tag"
category: "5. Container Security (Local)"
status: todo
related:
  - docs/local/containers/container-00-multi-stage-application-images-and-runtime-hardening.md
---

# Image versions pinned explicitly; no `latest` tag

## What
All images use explicit versions (ideally digests); `latest` is never used.

## Current state
`:latest` is used for Vault, Prometheus, Loki and Tempo, and `wispurl-vault:latest` locally. `postgres:18`, `redis:8` and `rabbitmq:4-management` float on major versions.

## Subtasks
- [ ] Pin Vault, Prometheus, Loki and Tempo to explicit versions
- [ ] Pin data stores to minor/patch versions
- [ ] Pin base images by digest (`python:3.13-slim@sha256:...`)
- [ ] Enable Dependabot/Renovate for Docker and Compose updates
- [ ] Enforce with hadolint DL3007 / Checkov in CI

## Acceptance criteria
- [ ] `grep -n ':latest' docker-compose.yml compose.observability.yaml */Dockerfile` returns nothing

## References
- [docker-compose.yml](../../../docker-compose.yml)
- [compose.observability.yaml](../../../compose.observability.yaml)
- [vault/Dockerfile](../../../vault/Dockerfile)
