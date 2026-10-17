---
id: LOC-7.12
title: "Chaos test: database connection exhaustion simulated and verified"
category: "7. Reliability and SRE (Local Validation)"
status: todo
related:
  - docs/local/sre/sre-03-local-failure-injection-and-chaos-validation.md
---

# Chaos test: database connection exhaustion simulated and verified

## What
Running out of database connections causes fast, bounded failures and clean recovery.

## Current state
Postgres `max_connections=200`; pool limits unverified.

## Subtasks
- [ ] Exhaust connections (pgbench or a script holding connections)
- [ ] Verify services fail fast (bounded `pool_timeout`) and `/ready` reports not ready
- [ ] Verify recovery once connections free
- [ ] Alert on connection usage; evaluate PgBouncer

## Acceptance criteria
- [ ] No hung requests during exhaustion, and full recovery afterwards
