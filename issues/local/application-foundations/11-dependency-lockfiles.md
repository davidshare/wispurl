---
id: LOC-1.11
title: "Strict dependency and version pinning (lockfiles)"
category: "1. Application Foundations"
status: done
related:
  - docs/local/app/app-00-dependency-lockfiles-and-reproducible-installs.md
---

# Strict dependency and version pinning (lockfiles)

## What
Every dependency is pinned via a lockfile and installs are reproducible byte-for-byte.

## Current state
Every Python service and shared library has a `uv.lock`; Dockerfiles use `uv sync --frozen` with a pinned uv image. The frontend has `package-lock.json`.

## Subtasks
- [x] `uv.lock` committed for every Python service and shared library
- [x] Docker builds use `uv sync --frozen` (fail if the lock is stale)
- [x] uv itself pinned (`ghcr.io/astral-sh/uv:0.11.7`)
- [x] Frontend `package-lock.json` committed

## Acceptance criteria
- [x] Rebuilding an image from the same commit installs identical package versions

## Notes
- Some `pyproject.toml` entries use `>=` (e.g. `hvac`, OpenTelemetry); the lock pins them, but tightening ranges makes upgrades more deliberate.

## References
- [auth-service/uv.lock](../../../auth-service/uv.lock)
- [frontend/package-lock.json](../../../frontend/package-lock.json)
