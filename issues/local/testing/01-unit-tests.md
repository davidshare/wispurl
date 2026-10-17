---
id: LOC-3.01
title: "Unit tests, run locally via Docker Compose"
category: "3. Testing"
status: todo
related:
  - docs/local/app/app-03-local-application-test-suite-and-coverage.md
---

# Unit tests, run locally via Docker Compose

## What
Each service has fast unit tests runnable locally through Docker Compose.

## Current state
No test files exist in any service.

## Subtasks
- [ ] Add `pytest`, `pytest-asyncio` and `respx` as dev dependencies per service
- [ ] Cover services, repositories, security (JWT, password hashing) and schemas
- [ ] Add a Compose `test` profile or `make test` that runs tests in containers
- [ ] Add frontend unit tests (e.g. Vitest) for API client and auth helpers

## Acceptance criteria
- [ ] `make test` runs all unit tests and exits non-zero on failure
