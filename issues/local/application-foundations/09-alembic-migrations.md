---
id: LOC-1.09
title: "Database migrations managed via Alembic (or Flyway/Liquibase)"
category: "1. Application Foundations"
status: done
related:
  - docs/local/app/app-01-database-migrations-and-repeatable-seed-data.md
---

# Database migrations managed via Alembic (or Flyway/Liquibase)

## What
Database schema changes are versioned migrations applied automatically and repeatably.

## Current state
auth, shortener and analytics each have an `alembic/` directory with versioned migrations; each entrypoint runs `alembic upgrade head` before starting.

## Subtasks
- [x] Alembic configured for auth-service, shortener-service and analytics-service
- [x] Initial migrations committed under `alembic/versions/`
- [x] Entrypoints run `alembic upgrade head` on start

## Acceptance criteria
- [x] A fresh database reaches the latest schema on first container start

## Notes
- Up/down migration tests are tracked in [Testing](../testing/04-migration-tests.md); moving migrations to a Kubernetes Job is in [Jobs and CronJobs](../kubernetes-packaging/18-jobs-and-cronjobs.md).

## References
- [auth-service/alembic](../../../auth-service/alembic)
- [auth-service/entrypoint.sh](../../../auth-service/entrypoint.sh)
