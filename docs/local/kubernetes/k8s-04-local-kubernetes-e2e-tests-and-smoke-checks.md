---
id: local-027
title: Local Kubernetes E2E tests and smoke checks
type: feat
feature: 3. Testing
status: not_started
depends_on: [local-016, local-017, local-018]
checklist_sections: 3. Testing; 4. Local CI/CD Pipeline
---

# Local Kubernetes E2E tests and smoke checks

## Goal
Verify the deployed WispURL user journey on Kind after ArgoCD sync.

## Implementation subtasks
- [ ] Wait for all required ArgoCD applications and pod probes
- [ ] run browser/API journey for registration/login, short-link creation and redirect, analytics event delivery/query, QR generation, and rate limiting
- [ ] assert public traffic enters through gateway and internal-only APIs are not reachable from outside namespace
- [ ] run post-deploy smoke tests and capture logs/traces on failure.

## Acceptance criteria
- [ ] Fresh Kind deployment becomes healthy
- [ ] all specified journeys pass
- [ ] a direct external request to analytics/rate-limiter internal endpoint is denied
- [ ] failed dependency causes smoke job to fail with useful diagnostics
- [ ] teardown cleans ephemeral test namespace/data

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
