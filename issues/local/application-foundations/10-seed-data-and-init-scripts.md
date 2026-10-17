---
id: LOC-1.10
title: "Seed data and repeatable local initialization scripts"
category: "1. Application Foundations"
status: partial
related:
  - docs/local/app/app-01-database-migrations-and-repeatable-seed-data.md
---

# Seed data and repeatable local initialization scripts

## What
A fresh clone reaches a working, demo-ready stack with a small number of repeatable commands, including sample data.

## Current state
`db/init/create-databases.sh` idempotently creates `auth_db`, `short_db`, `stats_db`; `vault-bootstrap.sh` seeds secrets and AppRoles. There is no application seed data and no single init/reset command.

## Subtasks
- [x] Idempotent database creation script
- [x] Vault secret and AppRole seeding
- [ ] Add an idempotent seed script (demo user, sample links, click events)
- [ ] Guard seeding so it only runs when `ENVIRONMENT=development`
- [ ] Add `make init` (certs → Vault → bootstrap → compose up → seed) and `make seed`
- [ ] Add `make reset` that wipes local data deliberately and documents what it deletes

## Acceptance criteria
- [ ] Fresh clone to logged-in demo with documented commands only
- [ ] Running the seed twice creates no duplicates

## References
- [db/init/create-databases.sh](../../../db/init/create-databases.sh)
- [vault/vault-bootstrap.sh](../../../vault/vault-bootstrap.sh)
- [Makefile](../../../Makefile)
