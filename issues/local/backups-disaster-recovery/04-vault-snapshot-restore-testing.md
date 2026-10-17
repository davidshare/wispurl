---
id: LOC-8.04
title: "Vault snapshot restore testing executed"
category: "8. Backups and Disaster Recovery (Local)"
status: todo
related:
  - docs/local/sre/sre-05-postgresql-vault-and-rabbitmq-recovery-runbooks.md
---

# Vault snapshot restore testing executed

## What
A Vault snapshot restore is executed and verified.

## Current state
None — see [Secrets → restore drill](../secrets-management/19-vault-snapshot-restore-drill.md) (same work).

## Subtasks
- [ ] Implement `make vault-restore`
- [ ] Canary secret drill (write → snapshot → delete → restore → verify)
- [ ] Record timing and steps

## Acceptance criteria
- [ ] Drill executed with evidence
