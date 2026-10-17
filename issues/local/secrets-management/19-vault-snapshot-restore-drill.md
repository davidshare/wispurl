---
id: LOC-2.19
title: "Vault snapshot restore drill executed at least once (cross-ref Section 7)"
category: "2. Secrets Management (Local)"
status: todo
related:
  - docs/local/sre/sre-05-postgresql-vault-and-rabbitmq-recovery-runbooks.md
---

# Vault snapshot restore drill executed at least once (cross-ref Section 7)

## What
Prove a Vault snapshot can actually be restored.

## Current state
No restore target or drill.

## Subtasks
- [ ] Add `make vault-restore SNAPSHOT=...` (`vault operator raft snapshot restore -force`)
- [ ] Drill: write a canary secret → snapshot → delete canary → restore → verify canary
- [ ] Confirm services re-authenticate after restore
- [ ] Record duration and steps in the Vault recovery runbook

## Acceptance criteria
- [ ] Drill executed with timing evidence
