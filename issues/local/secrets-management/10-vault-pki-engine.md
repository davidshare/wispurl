---
id: LOC-2.10
title: "Vault PKI engine configured for internal TLS issuance (optional at local scale)"
category: "2. Secrets Management (Local)"
status: todo
related:
  - docs/local/security/security-02-local-vault-deployment-engines-identity-and-lifecycle.md
---

# Vault PKI engine configured for internal TLS issuance (optional at local scale)

## What
Optionally issue internal TLS certificates from Vault PKI instead of hand-made OpenSSL certs.

## Current state
Vault's own cert comes from `vault/generate-certs.sh`; no PKI engine.

## Subtasks
- [ ] Enable a root and an intermediate PKI mount
- [ ] Create a role for `*.wispurl.local` / internal service names with short TTLs
- [ ] Issue a certificate for one internal endpoint (e.g. ingress or Postgres) and verify the chain
- [ ] Or record the decision to defer to cert-manager/mkcert

## Acceptance criteria
- [ ] A certificate issued by Vault PKI is served and validates against the Vault CA, or the deferral is documented
