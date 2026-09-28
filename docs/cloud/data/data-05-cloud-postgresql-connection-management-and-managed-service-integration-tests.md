---
id: cloud-024
title: Cloud PostgreSQL connection management and managed-service integration tests
type: feat
feature: 3. Testing
status: not_started
depends_on: [cloud-006, cloud-008]
checklist_sections: 3. Testing; 9. Infrastructure as Code
---

# Cloud PostgreSQL connection management and managed-service integration tests

## Goal
Validate application integration with AWS-managed stateful services and prevent connection exhaustion.

## Implementation subtasks
- [ ] Run staging E2E against RDS, ElastiCache and Amazon MQ from EKS
- [ ] set per-service DB pool limits whose sum is below RDS max connections
- [ ] test PgBouncer or RDS Proxy decision with measured connection churn
- [ ] verify TLS and IAM/secret auth
- [ ] run migration up/down on disposable DB
- [ ] assert broker DLQ and Redis outage behavior.

## Acceptance criteria
- [ ] Integration suite proves each workload reaches only its assigned dependency
- [ ] TLS/auth failure is rejected
- [ ] aggregate DB pool remains below configured limit under test load
- [ ] migration and rollback procedure succeeds
- [ ] dependency outage produces expected alert and service behavior

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
