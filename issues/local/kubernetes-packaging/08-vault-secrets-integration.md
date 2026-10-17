---
id: LOC-9.08
title: "Local secret management integrated with local Vault (via External Secrets Operator) or Kubernetes Secrets — see Section 2 for the Vault side of this"
category: "9. Local Kubernetes and Packaging"
status: todo
related:
  - docs/local/security/security-07-local-vault-secrets-integration-with-kubernetes.md
---

# Local secret management integrated with local Vault (via External Secrets Operator) or Kubernetes Secrets — see Section 2 for the Vault side of this

## What
Pods get secrets from local Vault (External Secrets Operator, Vault Secrets Operator or Agent Injector) — never from git.

## Current state
None.

## Subtasks
- [ ] Choose ESO (Vault provider), VSO or the Agent Injector and record why
- [ ] Enable the Vault Kubernetes auth method
- [ ] Create a Vault role per service bound to its ServiceAccount + namespace
- [ ] Create ExternalSecret/VaultStaticSecret per service
- [ ] Verify a rotated secret reaches pods

## Acceptance criteria
- [ ] Pods start with Vault-sourced secrets, and no Secret manifests are in git
