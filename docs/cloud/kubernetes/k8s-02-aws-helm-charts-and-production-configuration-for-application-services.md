---
id: cloud-016
title: AWS Helm charts and production configuration for application services
type: feat
feature: 1. Application Foundations
status: not_started
depends_on: [cloud-015]
checklist_sections: 1. Application Foundations; 10. Cloud Kubernetes
---

# AWS Helm charts and production configuration for application services

## Goal
Deploy all WispURL workloads to EKS using Helm with production-style but demonstrator-sized settings.

## Implementation subtasks
- [ ] Cover gateway, frontend, auth, shortener, analytics API/consumer, cleanup, notification, QR and rate limiter
- [ ] separate environment values
- [ ] place pods in private subnets where applicable
- [ ] set probes, resource requests/limits, non-root/read-only security contexts, PDB for replicated stateless services, HPA where metrics justify
- [ ] route only public gateway/frontend
- [ ] configure CORS/security headers
- [ ] use External Secrets references for DB, Redis, RabbitMQ, JWT and internal keys
- [ ] use PgBouncer/RDS Proxy only after connection budget demonstrates need
- [ ] run cleanup as CronJob.

## Acceptance criteria
- [ ] All charts render and ArgoCD deploys
- [ ] every pod is non-root, bounded and healthy
- [ ] no secret literals in chart/default values
- [ ] direct internal services are inaccessible externally
- [ ] CORS permits only configured frontend origins
- [ ] migration/cleanup jobs are ordered and idempotent
- [ ] autoscaling does not exceed documented account budget

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
