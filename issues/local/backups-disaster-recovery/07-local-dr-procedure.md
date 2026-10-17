---
id: LOC-8.07
title: "Local disaster recovery procedure documented"
category: "8. Backups and Disaster Recovery (Local)"
status: todo
related:
  - docs/local/sre/sre-05-postgresql-vault-and-rabbitmq-recovery-runbooks.md
---

# Local disaster recovery procedure documented

## What
A documented, drilled procedure rebuilds the whole local environment from backups.

## Current state
README covers resets only.

## Subtasks
- [ ] Write `docs/runbooks/disaster-recovery.md`: prerequisites (offline key backup), rebuild order (certs → Vault restore + unseal → Postgres → RabbitMQ definitions → Redis → apps → verify)
- [ ] Run an end-to-end drill from a wiped environment
- [ ] Record gaps found

## Acceptance criteria
- [ ] Full environment recovered from backups following only the document
