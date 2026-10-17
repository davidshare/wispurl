---
id: LOC-2.07
title: "Vault KV v2 secrets engine configured for application secrets"
category: "2. Secrets Management (Local)"
status: done
related:
  - docs/local/security/security-02-local-vault-deployment-engines-identity-and-lifecycle.md
---

# Vault KV v2 secrets engine configured for application secrets

## What
Application secrets live in a versioned KV v2 engine.

## Current state
Bootstrap enables KV v2 at `secret/` and writes one secret per service at `secret/wispurl/<service>`.

## Subtasks
- [x] Enable KV v2 at `secret/`
- [x] Write per-service secret documents

## Acceptance criteria
- [x] `vault kv get secret/wispurl/auth-service` shows versioned data

## References
- [vault/vault-bootstrap.sh](../../../vault/vault-bootstrap.sh)
