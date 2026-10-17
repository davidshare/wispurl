---
id: LOC-2.12
title: "Secret rotation process defined and tested at least once (manual is fine locally)"
category: "2. Secrets Management (Local)"
status: todo
related:
  - docs/local/security/security-02-local-vault-deployment-engines-identity-and-lifecycle.md
---

# Secret rotation process defined and tested at least once (manual is fine locally)

## What
A defined, tested process exists to rotate every secret type without an outage.

## Current state
No rotation procedure. AppRole `secret_id`s never expire (`secret_id_ttl=0`).

## Subtasks
- [ ] Write a rotation procedure per secret: JWT_SECRET, INTERNAL_API_KEY, DB passwords, RabbitMQ credentials, AppRole secret_id, root token
- [ ] Set a finite `secret_id_ttl` and add a reissue target
- [ ] Rotate INTERNAL_API_KEY once with `vault kv patch` + rolling restart and record the steps
- [ ] Verify the old value is rejected after rotation
- [ ] Link the procedure from the Vault recovery runbook

## Acceptance criteria
- [ ] One rotation executed end to end with evidence, and services stay healthy during it
