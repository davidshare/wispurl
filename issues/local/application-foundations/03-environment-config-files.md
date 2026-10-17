---
id: LOC-1.03
title: "Separate configuration files for development, staging, and production environments"
category: "1. Application Foundations"
status: todo
related:
  - docs/local/docker/docker-00-environment-configuration-and-safe-local-examples.md
---

# Separate configuration files for development, staging, and production environments

## What
Development, staging and production settings are defined separately so environment differences are explicit, reviewable and never hand-edited at deploy time.

## Current state
There is a single `.env.example`; `vault-bootstrap.sh` seeds Vault from `.env`. Services read settings via pydantic-settings with no environment profile, and `/docs` is enabled everywhere.

## Subtasks
- [ ] Add an `ENVIRONMENT` setting (`development` | `staging` | `production`) to every service config
- [ ] Create placeholder-only example files per environment (e.g. `config/development.env.example`, `staging`, `production`)
- [ ] Add a Compose override for development-only behaviour (debug ports, hot reload)
- [ ] Namespace Vault paths per environment (`secret/wispurl/<env>/<service>`) and update policies/bootstrap
- [ ] Disable `/docs` and `/redoc` and set stricter CORS when `ENVIRONMENT=production`
- [ ] Fail fast at startup when a required setting is missing
- [ ] Document which values differ per environment and why

## Acceptance criteria
- [ ] Starting a service with `ENVIRONMENT=staging` loads staging values without code changes
- [ ] No committed file contains a real secret (`make scan` passes)

## References
- [.env.example](../../../.env.example)
- [vault/vault-bootstrap.sh](../../../vault/vault-bootstrap.sh)
