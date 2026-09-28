---
id: cloud-006
title: Amazon RDS PostgreSQL for WispURL data
type: feat
feature: 9. Infrastructure as Code
status: not_started
depends_on: [cloud-001, cloud-002]
checklist_sections: 9. Infrastructure as Code; 8. Backups and Disaster Recovery
---

# Amazon RDS PostgreSQL for WispURL data

## Goal
Provision production-style PostgreSQL databases for auth, short links, and analytics without public access.

## Implementation subtasks
- [ ] Use private subnets and security groups scoped to EKS node/pod access
- [ ] separate databases/users by service
- [ ] enable encryption with KMS, automated backups and point-in-time recovery, deletion protection for retained environments, log exports and maintenance window
- [ ] set connection limits and PgBouncer or RDS Proxy evaluation
- [ ] configure credential rotation through Secrets Manager
- [ ] include RDS cost in demo teardown plan.

## Acceptance criteria
- [ ] Only intended EKS workloads connect
- [ ] service DB roles cannot access other service databases
- [ ] encryption and backup/PITR settings are inspectable
- [ ] restore a snapshot to isolated recovery DB and run migrations/smoke query
- [ ] connection pool stays under DB max
- [ ] public connectivity is disabled

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
