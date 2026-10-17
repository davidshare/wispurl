---
id: LOC-6.08
title: "Centralized log aggregation with Loki"
category: "6. Observability (Local Stack)"
status: done
related:
  - docs/local/observability/obs-01-centralized-logs-with-loki-and-alloy.md
---

# Centralized log aggregation with Loki

## What
Loki stores logs from all project containers.

## Current state
Loki runs with filesystem TSDB (schema v13), loopback API and a healthcheck.

## Subtasks
- [x] Loki service with persistent volume
- [x] Filesystem TSDB schema
- [x] Healthcheck and loopback port

## Acceptance criteria
- [x] Logs for every project container are queryable via the Loki API

## Notes
- Retention is currently not enforced — see [Retention limits](../cost-capacity/03-retention-limits.md).
- The query-results cache was also removed on the branch; optional at local scale, so not tracked.

## Follow-ups
- [ ] Restore `reject_old_samples: true` and `reject_old_samples_max_age: 168h` in `limits_config` (removed on `ops/add-grafana-alloy-docker-compose`) so replayed/old logs can't bypass retention

## References
- [observability/loki/loki.yaml](../../../observability/loki/loki.yaml)
