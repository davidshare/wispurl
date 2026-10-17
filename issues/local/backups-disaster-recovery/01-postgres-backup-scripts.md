---
id: LOC-8.01
title: "PostgreSQL automated local backup scripts (pg_dump)"
category: "8. Backups and Disaster Recovery (Local)"
status: todo
related:
  - docs/local/sre/sre-00-local-database-backup-and-restore.md
---

# PostgreSQL automated local backup scripts (`pg_dump`)

## What
Automated local PostgreSQL backups with `pg_dump`.

## Current state
None.

## Subtasks
- [ ] `scripts/backup-postgres.sh`: `pg_dump -Fc` per database (`auth_db`, `short_db`, `stats_db`) plus `pg_dumpall --globals-only`
- [ ] Timestamped files in a gitignored `backups/postgres/` with checksums
- [ ] Retention (keep last N)
- [ ] `make db-backup` and a schedule (cron or a Compose sidecar)

## Acceptance criteria
- [ ] Backups appear on schedule and old ones are pruned
