---
id: local-001
title: Docker Compose local stack baseline
type: feat
feature: 1. Application Foundations
status: verify
depends_on: []
checklist_sections: 1. Application Foundations
---

# Docker Compose local stack baseline

## Goal
Audit and make the root Docker Compose stack the documented one-command local application environment. Preserve the existing service topology: PostgreSQL with separate databases, Redis, RabbitMQ, Vault, Python services, gateway, and frontend.

## Implementation subtasks
- [ ] Enumerate required environment variables and safe defaults
- [ ] fail with a readable message for missing required secrets
- [ ] keep host-published development ports bound to loopback
- [x] preserve dependency health gates
- [ ] ensure persistent data volumes and repeatable database initialization
- [ ] pin every third-party image to an explicit supported version (no latest tags)
- [ ] document startup, status, logs, stop, and reset behavior
- [ ] ensure the separate observability Compose project can join the application network without requiring it to exist before startup.

## Acceptance criteria
- [ ] A clean checkout can start the documented stack after copying the env template
- [ ] all expected services become healthy
- [ ] service data survives stop/start
- [ ] reset behavior is explicit
- [ ] ports are local-only where intended
- [ ] every image uses an explicit version or digest and none uses latest
- [ ] Compose config validation reports no unresolved references
- [ ] README and checklist match actual behavior

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
