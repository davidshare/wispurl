---
id: LOC-12.03
title: "Local log and metric retention limits configured to prevent disk exhaustion"
category: "12. Cost and Capacity Management (Local)"
status: partial
related:
  - docs/local/sre/sre-04-local-load-and-capacity-baseline-plus-retention-limits.md
---

# Local log and metric retention limits configured to prevent disk exhaustion

## What
Logs, metrics, traces and local artefacts have bounded retention so disks don't fill.

## Current state
Prometheus keeps 15d and Tempo keeps 744h blocks. Loki's `retention_period` is set, but this branch removed the compactor block, so nothing is deleted. Docker logs, the Vault audit log and backups are unbounded.

## Subtasks
- [x] Prometheus time retention (15d)
- [x] Tempo block retention (744h)
- [x] Restore Loki `compactor` with `retention_enabled: true` and `delete_request_store: filesystem`
- [x] Add Prometheus `--storage.tsdb.retention.size`
- [ ] Set Docker `logging` options (`max-size`, `max-file`) on every service (done for the observability stack; app stack still open)
- [ ] Rotate the Vault audit log
- [ ] Retention for backups and snapshots

## Acceptance criteria
- [ ] Disk usage plateaus over a multi-day run

## References
- [observability/loki/loki.yaml](../../../observability/loki/loki.yaml)
- [compose.observability.yaml](../../../compose.observability.yaml)
