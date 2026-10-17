---
id: LOC-2.05
title: "Vault policies defined per service/team (least privilege, not root-token-everywhere)"
category: "2. Secrets Management (Local)"
status: done
related:
  - docs/local/security/security-02-local-vault-deployment-engines-identity-and-lifecycle.md
---

# Vault policies defined per service/team (least privilege, not root-token-everywhere)

## What
Each service gets a least-privilege policy that reads only its own secret path; no service uses the root token.

## Current state
Bootstrap writes one policy per service granting `read` on `secret/data/wispurl/<service>` and its metadata, plus `renew-self`.

## Subtasks
- [x] Policy per service scoped to its own KV path
- [x] Read-only capabilities
- [x] Services authenticate with AppRole tokens bound to their policy, never root

## Acceptance criteria
- [x] A service token cannot read another service's path (403)

## Notes
- `make vault-env` uses the root token for developer convenience; consider a developer policy instead.

## References
- [vault/vault-bootstrap.sh](../../../vault/vault-bootstrap.sh)
