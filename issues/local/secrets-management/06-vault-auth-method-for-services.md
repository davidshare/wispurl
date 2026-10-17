---
id: LOC-2.06
title: "Vault auth method configured for services (AppRole locally; Kubernetes auth once local k8s is up)"
category: "2. Secrets Management (Local)"
status: done
related:
  - docs/local/security/security-03-application-services-authenticate-to-vault-and-consume-scoped-secrets.md
---

# Vault auth method configured for services (AppRole locally; Kubernetes auth once local k8s is up)

## What
Services authenticate to Vault with a machine auth method — AppRole locally, Kubernetes auth once the cluster exists.

## Current state
AppRole enabled; one role per service (token TTL 1h, max 4h). Credentials are written to `vault/approles/<service>.json` and mounted as Compose secrets; `shared/vault_client` logs in and loads the service's secrets.

## Subtasks
- [x] Enable AppRole
- [x] Role per service bound to its policy
- [x] Deliver role_id/secret_id as Compose secrets
- [x] Shared `vault_client` logs in and loads secrets at startup

## Acceptance criteria
- [x] Every service starts and reads its config from Vault using its own AppRole

## Notes
- `secret_id_ttl=0` and unlimited uses — tighten in [Secret rotation](12-secret-rotation.md).
- Kubernetes auth is tracked in [Secrets integration](../kubernetes-packaging/08-vault-secrets-integration.md).

## Follow-ups
- [ ] Remove the `shortener-service-approle` and `vault-ca` secrets from the `frontend` service in `docker-compose.yml` — the frontend never talks to Vault, so it should hold no Vault credentials (least privilege)

## References
- [shared/vault_client/src/vault_client/client.py](../../../shared/vault_client/src/vault_client/client.py)
- [docker-compose.yml](../../../docker-compose.yml)
