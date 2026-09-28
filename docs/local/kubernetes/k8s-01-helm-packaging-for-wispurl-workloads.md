---
id: local-017
title: Helm packaging for WispURL workloads
type: feat
feature: 9. Local Kubernetes and Packaging
status: not_started
depends_on: [local-016]
checklist_sections: 9. Local Kubernetes and Packaging
---

# Helm packaging for WispURL workloads

## Goal
Package every stateless service and stateful dependency used in the Kubernetes demo as maintainable Helm charts with environment-specific values.

## Implementation subtasks
- [ ] Create charts for gateway, frontend, auth, shortener, analytics API/consumer, cleanup, notification, QR, and rate limiter
- [ ] chart PostgreSQL, Redis, RabbitMQ, Vault and observability only where they are intentionally in-cluster
- [ ] define Deployment/Service/ConfigMap/Secret references, startup/readiness/liveness probes, requests/limits, securityContext, PodDisruptionBudget where meaningful, PVCs for stateful components, Jobs/CronJobs for cleanup and database initialization
- [ ] separate local, staging, production values and prohibit secret literals in values.

## Acceptance criteria
- [ ] All chart templates render for local values
- [ ] schema validation catches missing required values
- [ ] all application workloads run with restricted security context and resource requests/limits
- [ ] cleanup runs as a CronJob
- [ ] persistent state has PVC
- [ ] no plaintext credential exists in chart defaults
- [ ] documented upgrade/uninstall behavior preserves or intentionally removes PVC data

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
