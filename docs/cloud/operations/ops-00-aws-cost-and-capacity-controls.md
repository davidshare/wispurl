---
id: cloud-023
title: AWS cost and capacity controls
type: feat
feature: 13. Cost and Capacity Management
status: not_started
depends_on: [cloud-001, cloud-018]
checklist_sections: 13. Cost and Capacity Management
---

# AWS cost and capacity controls

## Goal
Prevent portfolio infrastructure from accruing unbounded cost while still demonstrating production-style scaling and observability.

## Implementation subtasks
- [ ] Produce pre-provision estimates for EKS, NAT, RDS, ElastiCache, Amazon MQ, ALB, AMP/Grafana/CloudWatch/X-Ray, ECR and S3
- [ ] use AWS Cost Explorer and Infracost pull-request estimates
- [ ] set budget notifications
- [ ] select small instance classes, min node counts and auto-stop/teardown schedule
- [ ] monitor storage growth, DB connections, log/metric retention and utilization
- [ ] schedule right-size review after load run
- [ ] record which managed services continue charging while idle.

## Acceptance criteria
- [ ] Estimate is reviewed before apply
- [ ] budget alarm is tested
- [ ] scheduled teardown removes billable compute while retaining only intentionally persistent protected state
- [ ] storage/connection/retention alarms fire at test thresholds
- [ ] right-size report records actual cost versus estimate and next adjustment

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
