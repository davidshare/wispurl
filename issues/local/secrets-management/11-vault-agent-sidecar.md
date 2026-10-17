---
id: LOC-2.11
title: "Vault Agent or Agent Injector sidecar pattern tested locally"
category: "2. Secrets Management (Local)"
status: todo
related:
  - docs/local/security/security-02-local-vault-deployment-engines-identity-and-lifecycle.md
---

# Vault Agent or Agent Injector sidecar pattern tested locally

## What
Test the Vault Agent pattern locally: a sidecar authenticates and renders secrets to a file so the app never handles Vault auth.

## Current state
Services call Vault directly through `shared/vault_client`.

## Subtasks
- [ ] Run Vault Agent as a sidecar for one service in Compose with `auto_auth` (AppRole)
- [ ] Render the service's secrets to a templated file on a shared volume
- [ ] Make the service read config from that file
- [ ] Verify token renewal and re-render on secret change
- [ ] Repeat with the Agent Injector once the kind cluster exists

## Acceptance criteria
- [ ] The pilot service runs with no Vault code path, and changing the secret updates the rendered file
