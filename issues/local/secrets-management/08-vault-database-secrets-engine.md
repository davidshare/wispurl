---
id: LOC-2.08
title: "Vault Database secrets engine configured for dynamic, short-lived DB credentials"
category: "2. Secrets Management (Local)"
status: todo
related:
  - docs/local/security/security-02-local-vault-deployment-engines-identity-and-lifecycle.md
---

# Vault Database secrets engine configured for dynamic, short-lived DB credentials

## What
Services receive short-lived, per-instance Postgres credentials from Vault instead of a shared static password.

## Current state
Services use static `DATABASE_URL`s stored in KV, each with its own least-privilege login (`auth_svc`, `shortener_svc`, `analytics_svc`, `cleanup_svc`) rather than the superuser. These static passwords are what the database secrets engine would replace with short-lived ones; the roles' grants are a ready-made template for the engine's creation statements.

## Subtasks
- [ ] Enable the `database` secrets engine and configure the Postgres connection with a dedicated Vault admin role
- [ ] Create roles per database (`auth_db`, `short_db`, `stats_db`) with minimal grants and a 1h TTL
- [ ] Use a separate role for migrations (DDL) vs runtime (DML)
- [ ] Update service policies to read `database/creds/<role>`
- [ ] Teach `vault_client` to fetch and renew/re-fetch DB credentials and rebuild the SQLAlchemy engine
- [ ] Rotate the root credential so only Vault knows it

## Acceptance criteria
- [ ] `pg_stat_activity` shows Vault-generated usernames for each service
- [ ] Revoking a lease cuts that service's DB access, and it recovers with new credentials
