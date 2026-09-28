---
id: cloud-025
title: Cloud deployment smoke tests and rollback verification
type: feat
feature: 3. Testing
status: not_started
depends_on: [cloud-011, cloud-015, cloud-018]
checklist_sections: 3. Testing; 4. Cloud CI/CD
---

# Cloud deployment smoke tests and rollback verification

## Goal
Gate every EKS promotion on production-like smoke tests and verify a safe rollback path.

## Implementation subtasks
- [ ] After ArgoCD reports Healthy, exercise registration/login, create/redirect link, analytics event and query, QR generation, rate-limit behavior, health endpoints and TLS
- [ ] verify trace/log/metric emission
- [ ] inject a known unhealthy image or failing readiness check in a staging namespace
- [ ] ensure promotion halts and revert via GitOps.

## Acceptance criteria
- [ ] Successful deployment passes all checks and records image digest
- [ ] unhealthy rollout blocks promotion and triggers documented rollback
- [ ] previous revision becomes healthy
- [ ] failed smoke output identifies endpoint and correlation ID
- [ ] no direct unreviewed kubectl deployment is needed

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
