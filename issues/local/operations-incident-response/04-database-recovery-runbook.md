---
id: LOC-11.04
title: "Local database recovery runbook created"
category: "11. Operations and Incident Response (Local)"
status: todo
related:
  - docs/local/sre/sre-05-postgresql-vault-and-rabbitmq-recovery-runbooks.md
---

# Local database recovery runbook created

## What
Runbook for recovering PostgreSQL.

## Current state
None.

## Subtasks
- [ ] Scenarios: container won't start, corrupted volume, bad migration, accidental delete
- [ ] Restore from `pg_dump` backup step by step
- [ ] Verification and service restart order

## Acceptance criteria
- [ ] Restore drill performed from the runbook
