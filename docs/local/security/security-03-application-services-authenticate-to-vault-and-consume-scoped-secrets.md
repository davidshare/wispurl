---
id: local-008
title: Application services authenticate to Vault and consume scoped secrets
type: feat
feature: 2. Secrets Management
status: not_started
depends_on: [local-007]
checklist_sections: 2. Secrets Management; 1. Application Foundations
---

# Application services authenticate to Vault and consume scoped secrets

## Goal
Integrate the existing shared Vault client and per-service AppRole files so service startup consumes its own Vault KV v2 values, not root credentials or copied application secrets.

## Implementation subtasks
- [ ] Cover auth-service, shortener-service, analytics-service, analytics-consumer-service, cleanup-service, notification-service, rate-limiter-service, QR service, and gateway
- [x] configure bootstrap policies so each AppRole is scoped to its own secret path
- [ ] reconcile seed keys and types with runtime settings, including DB URLs, JWT_SECRET, INTERNAL_API_KEY, RabbitMQ, Redis, SMTP_USERNAME, and service URLs
- [ ] fail startup closed with a safe diagnostic if Vault auth/read fails or required values are absent
- [ ] never log role secret IDs, root token, or returned values
- [x] mount AppRole files and CA read-only using Compose secrets
- [ ] align make vault-env output with actual Compose consumption or remove the misleading path.

## Acceptance criteria
- [ ] Every listed service starts using its own AppRole
- [ ] wrong role/path is denied
- [ ] missing Vault or required secret prevents unsafe startup and produces a redacted error
- [ ] credentials are not environment variables baked into image layers
- [ ] service policy cannot read another service’s path
- [ ] documented rotation/restart procedure is exercised for one DB credential and one application secret

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
