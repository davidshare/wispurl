---
id: LOC-8.03
title: "HashiCorp Vault Raft snapshots configured locally"
category: "8. Backups and Disaster Recovery (Local)"
status: done
related:
  - docs/local/sre/sre-05-postgresql-vault-and-rabbitmq-recovery-runbooks.md
---

# HashiCorp Vault Raft snapshots configured locally

## What
Vault Raft snapshots are configured locally.

## Current state
`make vault-snapshot` writes timestamped snapshots to `vault/snapshots/` (same capability as the Secrets item).

## Subtasks
- [x] Snapshot target
- [x] Snapshot directory persisted and gitignored

## Acceptance criteria
- [x] A `.snap` file is produced on demand

## Notes
- Schedule snapshots and copy them off-host (encrypted).

## References
- [Makefile](../../../Makefile)
