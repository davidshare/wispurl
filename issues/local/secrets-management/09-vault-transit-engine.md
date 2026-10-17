---
id: LOC-2.09
title: "Vault Transit engine configured if any encryption-as-a-service need exists"
category: "2. Secrets Management (Local)"
status: todo
related:
  - docs/local/security/security-02-local-vault-deployment-engines-identity-and-lifecycle.md
---

# Vault Transit engine configured if any encryption-as-a-service need exists

## What
Use Vault Transit for encryption-as-a-service if any data needs application-level encryption; otherwise record why not.

## Current state
Not configured. Candidates: user emails / PII, IP data before anonymisation in analytics.

## Subtasks
- [ ] Decide and document whether any data requires app-level encryption
- [ ] If yes: enable Transit, create a named key, and grant `encrypt`/`decrypt` only to the owning service
- [ ] If yes: encrypt/decrypt the chosen field via Transit
- [ ] If yes: rotate the key and confirm old ciphertext still decrypts

## Acceptance criteria
- [ ] Decision recorded; if implemented, the stored value is ciphertext and key rotation is verified
