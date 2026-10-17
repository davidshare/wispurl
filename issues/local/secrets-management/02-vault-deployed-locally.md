---
id: LOC-2.02
title: "HashiCorp Vault deployed and running locally"
category: "2. Secrets Management (Local)"
status: done
related:
  - docs/local/security/security-02-local-vault-deployment-engines-identity-and-lifecycle.md
---

# HashiCorp Vault deployed and running locally

## What
HashiCorp Vault runs locally with Raft storage and TLS so services fetch secrets from Vault, not `.env` files.

## Current state
Custom `wispurl-vault` image, Raft storage in `vault/data`, TLS from a local CA (`make vault-certs`), UI/API on loopback, and a `vault-unseal` sidecar. Managed via `make vault-up/status/down/clean`.

## Subtasks
- [x] Vault service with Raft storage and persistent data directory
- [x] TLS listener with locally generated CA and server certificate
- [x] Ports bound to `127.0.0.1`
- [x] Make targets for lifecycle

## Acceptance criteria
- [x] `make vault-status` reports initialized and unsealed

## Notes
- Vault image is unpinned (`hashicorp/vault:latest`) — tracked in [Pin image versions](../container-security/07-pin-image-versions.md).

## References
- [vault/Dockerfile](../../../vault/Dockerfile)
- [vault/config/vault.hcl](../../../vault/config/vault.hcl)
- [vault/generate-certs.sh](../../../vault/generate-certs.sh)
