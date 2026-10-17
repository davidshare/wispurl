---
id: LOC-5.01
title: "Minimal base images (distroless, alpine)"
category: "5. Container Security (Local)"
status: done
related:
  - docs/local/containers/container-00-multi-stage-application-images-and-runtime-hardening.md
---

# Minimal base images (distroless, alpine)

## What
Runtime images use minimal bases to shrink attack surface.

## Current state
Python services use `python:3.13-slim`, the frontend uses `node:22-alpine`, and Vault uses the Alpine-based official image.

## Subtasks
- [x] Python runtime on `python:3.13-slim`
- [x] Frontend on `node:22-alpine`
- [x] No compilers or build tools in runtime stages

## Acceptance criteria
- [x] Runtime images contain no build toolchain

## Notes
- Distroless (`gcr.io/distroless/python3`) is a possible next step once health checks no longer rely on a shell/`python -c`.

## References
- [auth-service/Dockerfile](../../../auth-service/Dockerfile)
- [frontend/Dockerfile](../../../frontend/Dockerfile)
