---
id: LOC-3.04
title: "Database migration tests verifying up/down scripts"
category: "3. Testing"
status: todo
related:
  - docs/local/app/app-01-database-migrations-and-repeatable-seed-data.md
---

# Database migration tests verifying up/down scripts

## What
Every Alembic migration is proven to upgrade and downgrade cleanly.

## Current state
None.

## Subtasks
- [ ] For auth, shortener and analytics: upgrade head → downgrade base → upgrade head on an empty DB
- [ ] Run `alembic check` to detect model/migration drift
- [ ] Run in CI

## Acceptance criteria
- [ ] Migration round-trip passes for all three services
