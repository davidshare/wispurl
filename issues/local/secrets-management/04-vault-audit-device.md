---
id: LOC-2.04
title: "Vault audit device enabled (logs every secret access)"
category: "2. Secrets Management (Local)"
status: done
related:
  - docs/local/security/security-02-local-vault-deployment-engines-identity-and-lifecycle.md
---

# Vault audit device enabled (logs every secret access)

## What
Every Vault request is written to an audit log for traceability.

## Current state
`vault-bootstrap.sh` enables a file audit device at `/vault/logs/audit.log`, mounted to `vault/logs/` on the host.

## Subtasks
- [x] Enable file audit device in bootstrap
- [x] Persist audit log to host volume (gitignored)

## Acceptance criteria
- [x] Reading a secret produces an entry in `vault/logs/audit.log`

## Notes
- Ship the audit log to Loki and add rotation — see [Retention limits](../cost-capacity/03-retention-limits.md).

## References
- [vault/vault-bootstrap.sh](../../../vault/vault-bootstrap.sh)
