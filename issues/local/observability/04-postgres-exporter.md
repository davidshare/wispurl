---
id: LOC-6.04
title: "Database metrics (PostgreSQL exporter) configured"
category: "6. Observability (Local Stack)"
status: done
related:
  - docs/local/observability/obs-00-prometheus-metrics-collection-and-exporters.md
---

# Database metrics (PostgreSQL exporter) configured

## What
PostgreSQL metrics are collected.

## Current state
Alloy runs `prometheus.exporter.postgres` with the DSN read from a Docker secret and remote-writes to Prometheus.

## Subtasks
- [x] Postgres exporter configured in Alloy
- [x] DSN supplied via Docker secret file (gitignored)

## Acceptance criteria
- [x] `pg_up` = 1 and connection/transaction metrics are queryable

## Follow-ups
- [ ] Create a dedicated monitoring role (`LOGIN` + `pg_monitor`, no superuser) via `db/init/` or a migration-style script
- [ ] Point `observability/secrets/postgres_dsn.txt` at that role and update the README instructions
- [ ] Rotate the `postgres` superuser password, since it has been stored in that DSN file (update `.env`, the database URLs in Vault, and restart services)

## References
- [observability/alloy/config.alloy](../../../observability/alloy/config.alloy)
