---
id: LOC-1.08
title: "API documentation generated and served via OpenAPI/Swagger"
category: "1. Application Foundations"
status: done
---

# API documentation generated and served via OpenAPI/Swagger

## What
Each HTTP API publishes an OpenAPI schema and interactive docs generated from code.

## Current state
Every FastAPI service sets `docs_url=/docs` and `redoc_url=/redoc`; routes are tagged.

## Subtasks
- [x] `/docs`, `/redoc` and `/openapi.json` on all HTTP services
- [x] Routes grouped with tags

## Acceptance criteria
- [x] `/docs` renders for each service (gateway via `:8080/docs`)

## Notes
- Disabling docs in production is part of [Environment config](03-environment-config-files.md).

## References
- [gateway/app/main.py](../../../gateway/app/main.py)
