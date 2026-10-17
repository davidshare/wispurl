---
id: LOC-11.01
title: "Common local troubleshooting commands documented"
category: "11. Operations and Incident Response (Local)"
status: partial
related:
  - docs/local/sre/sre-06-local-operational-guide-and-troubleshooting.md
---

# Common local troubleshooting commands documented

## What
Common troubleshooting commands are documented by symptom.

## Current state
README and `make help` cover starting, status, logs and Vault basics; there's no symptom-based guide.

## Subtasks
- [x] Basic Compose and Vault commands in README and `make help`
- [ ] Write `docs/runbooks/troubleshooting.md` by symptom: Vault sealed, service unhealthy, gateway 502/504, RabbitMQ backlog, DLQ non-empty, Alloy not shipping, port conflicts
- [ ] Add kubectl equivalents once the cluster exists

## Acceptance criteria
- [ ] A newcomer can diagnose the listed symptoms using only the guide
