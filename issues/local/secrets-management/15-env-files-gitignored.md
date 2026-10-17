---
id: LOC-2.15
title: ".env files git-ignored; .env.example maintained with placeholder values"
category: "2. Secrets Management (Local)"
status: done
related:
  - docs/local/docker/docker-00-environment-configuration-and-safe-local-examples.md
---

# `.env` files git-ignored; `.env.example` maintained with placeholder values

## What
Real `.env` files never enter git; a placeholder `.env.example` documents every variable.

## Current state
`.gitignore` ignores `.env`, `.env.*`, `**/.env` (allowing `.env.example`) plus Vault keys, TLS, approles and observability secrets.

## Subtasks
- [x] Ignore `.env` variants, keep `.env.example`
- [x] Ignore Vault keys, data, TLS, approles, snapshots
- [x] `.env.example` maintained with placeholder values
- [x] README explains generating real values

## Acceptance criteria
- [x] `git check-ignore .env vault/keys/.vault-keys` matches both

## References
- [.gitignore](../../../.gitignore)
- [.env.example](../../../.env.example)
