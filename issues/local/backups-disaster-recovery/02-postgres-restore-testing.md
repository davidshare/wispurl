---
id: LOC-8.02
title: "PostgreSQL local restore testing documented and executed"
category: "8. Backups and Disaster Recovery (Local)"
status: todo
related:
  - docs/local/sre/sre-00-local-database-backup-and-restore.md
---

# PostgreSQL local restore testing documented and executed

## What
Restores are documented and actually executed.

## Current state
None.

## Subtasks
- [ ] `make db-restore DB=... FILE=...` restoring into a scratch database
- [ ] Verify with row counts and a canary record
- [ ] Measure restore duration
- [ ] Document the procedure in the database recovery runbook

## Acceptance criteria
- [ ] Restore drill executed with evidence and timing
