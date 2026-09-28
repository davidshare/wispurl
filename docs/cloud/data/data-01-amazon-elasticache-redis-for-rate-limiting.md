---
id: cloud-007
title: Amazon ElastiCache Redis for rate limiting
type: feat
feature: 9. Infrastructure as Code
status: not_started
depends_on: [cloud-001, cloud-002]
checklist_sections: 9. Infrastructure as Code; 7. Reliability and SRE
---

# Amazon ElastiCache Redis for rate limiting

## Goal
Provision private Redis-compatible cache for the rate limiter using a bounded portfolio configuration and explicit data-loss semantics.

## Implementation subtasks
- [ ] Use private subnet group and security groups scoped to rate-limiter workloads
- [ ] enable in-transit encryption and authentication where supported by selected engine
- [ ] define parameter group, maintenance and backup policy appropriate to ephemeral rate-limit state
- [ ] configure client TLS/timeouts
- [ ] expose metrics and alarms
- [ ] document whether fail-open or fail-closed behavior is selected when Redis is unavailable.

## Acceptance criteria
- [ ] Only rate-limiter identity/network path reaches Redis
- [ ] unauthenticated and out-of-VPC attempts fail
- [ ] TLS is verified by application
- [ ] restart/failover behavior matches documented rate-limit semantics
- [ ] CloudWatch metrics and alarm show memory/connections/CPU
- [ ] cost and teardown documented

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
