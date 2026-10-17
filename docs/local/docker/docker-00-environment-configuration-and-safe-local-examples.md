---
id: local-003
title: Environment configuration and safe local examples
type: feat
feature: 1. Application Foundations
status: not_started
depends_on: []
checklist_sections: 1. Application Foundations; 2. Secrets Management
---

# Environment configuration and safe local examples

## Goal
Define a consistent configuration contract across local development, test, staging, and production, with committed examples containing placeholders only.

## Implementation subtasks
- [ ] Inventory every variable consumed by Compose and service settings
- [ ] classify required secret, optional secret, and non-secret setting
- [ ] define precedence per environment
- [x] keep local-only values in ignored env files
- [ ] make .env.example complete and nonfunctional as a production credential
- [ ] remove contradictory names/defaults between root Compose, Vault seed data, service settings, and docs
- [ ] validate missing required values at startup.

## Acceptance criteria
- [ ] Each service configuration variable is documented with type, requirement, default, and environment
- [ ] clean checkout setup succeeds from the example after required local values are supplied
- [ ] no placeholder can silently authenticate in non-local environments
- [ ] Gitleaks passes on committed examples
- [ ] no secret appears in Compose defaults

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
