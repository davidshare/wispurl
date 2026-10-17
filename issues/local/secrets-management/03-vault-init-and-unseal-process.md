---
id: LOC-2.03
title: "Vault initialized with a secure key-shares/unseal process documented (even in dev mode, document what production unseal would look like)"
category: "2. Secrets Management (Local)"
status: done
related:
  - docs/local/security/security-02-local-vault-deployment-engines-identity-and-lifecycle.md
---

# Vault initialized with a secure key-shares/unseal process documented (even in dev mode, document what production unseal would look like)

## What
Vault is initialised with Shamir key shares, and both the local unseal flow and the production equivalent are documented.

## Current state
The sidecar initialises with 5 shares / threshold 3, writes keys to `vault/keys/.vault-keys` (mode 600, gitignored) and unseals with 3 keys. README states this is not a production KMS auto-unseal design.

## Subtasks
- [x] Initialise with 5 key shares and threshold 3
- [x] Store key material outside git with restrictive permissions
- [x] Automatic local unseal via sidecar
- [x] Document that production uses KMS auto-unseal and separate key custodians

## Acceptance criteria
- [x] After `docker compose restart vault`, the sidecar unseals Vault without manual steps

## Notes
- Worth expanding the production note (cloud KMS auto-unseal, recovery keys, custodian ceremony) when writing the cloud runbooks.

## References
- [vault/vault-unseal.sh](../../../vault/vault-unseal.sh)
- [vault/vault-init.sh](../../../vault/vault-init.sh)
- [README.md](../../../README.md)
