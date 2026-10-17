---
id: LOC-11.05
title: "Local Vault recovery runbook created"
category: "11. Operations and Incident Response (Local)"
status: todo
related:
  - docs/local/sre/sre-05-postgresql-vault-and-rabbitmq-recovery-runbooks.md
---

# Local Vault recovery runbook created

## What
Runbook for recovering Vault.

## Current state
None.

## Subtasks
- [ ] Scenarios: sealed after restart, sidecar failure, lost/corrupt Raft data, lost keys file, compromised AppRole
- [ ] Manual unseal, snapshot restore, AppRole reissue, root token rotation
- [ ] Verification that services re-authenticate

## Acceptance criteria
- [ ] Snapshot-restore drill performed from the runbook
