---
id: LOC-2.17
title: "Documented process for developers to pull secrets from Vault rather than sharing via Slack/email"
category: "2. Secrets Management (Local)"
status: done
related:
  - docs/local/security/security-02-local-vault-deployment-engines-identity-and-lifecycle.md
---

# Documented process for developers to pull secrets from Vault rather than sharing via Slack/email

## What
Developers pull secrets from Vault with a documented command instead of sharing them over chat or email.

## Current state
`make vault-env SERVICE=<name>` writes `<service>/.env` from Vault; documented in `make help` and the bootstrap output.

## Subtasks
- [x] `make vault-env` target
- [x] Documented in `make help` and bootstrap next steps
- [x] Generated files are gitignored

## Acceptance criteria
- [x] A developer can produce a working service `.env` with one command

## Notes
- Replacing the root token in `make vault-env` with a developer policy is tracked in [RBAC and least privilege](../security-compliance/01-rbac-least-privilege.md).

## Follow-ups
- [ ] Document `make vault-env SERVICE=<name>` in the README (when to use it, that output is gitignored, re-run after rotation)

## References
- [Makefile](../../../Makefile)
