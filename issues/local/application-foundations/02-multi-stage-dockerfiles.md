---
id: LOC-1.02
title: "Dockerfiles for every service using multi-stage builds"
category: "1. Application Foundations"
status: done
related:
  - docs/local/containers/container-00-multi-stage-application-images-and-runtime-hardening.md
---

# Dockerfiles for every service using multi-stage builds

## What
Every service image is built in stages so build tooling and caches never reach the runtime image.

## Current state
All 8 Python services use a `builder` stage (uv `sync --frozen` with a cache mount) and a slim `runtime` stage that copies only `/app`. The frontend uses `deps` → `builder` → `runner` stages.

## Subtasks
- [x] Builder stage installs dependencies with `uv sync --frozen --no-dev` and a BuildKit cache mount
- [x] Runtime stage copies only the built `/app` (venv + code) from the builder
- [x] Frontend uses separate deps/builder/runner stages
- [x] Each service has a `.dockerignore`

## Acceptance criteria
- [x] Every service builds with `docker compose build`
- [x] Runtime images contain no uv binary, build cache, or dev dependencies

## References
- [auth-service/Dockerfile](../../../auth-service/Dockerfile)
- [frontend/Dockerfile](../../../frontend/Dockerfile)
