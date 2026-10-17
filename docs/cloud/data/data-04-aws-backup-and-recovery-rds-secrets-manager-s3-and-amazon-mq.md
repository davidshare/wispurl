---
id: cloud-020
title: AWS backup and recovery: RDS, Secrets Manager, S3, and Amazon MQ
type: feat
feature: 8. Backups and Disaster Recovery
status: not_started
depends_on: [cloud-003, cloud-006, cloud-008, cloud-010]
checklist_sections: 8. Backups and Disaster Recovery
---

# AWS backup and recovery: RDS, Secrets Manager, S3, and Amazon MQ

## Goal
Define and prove recoverability for the project’s durable cloud data and configuration.

## Implementation subtasks
- [ ] Enable RDS point-in-time recovery and encrypted snapshots using AWS managed backup rather than adding WAL-G to RDS
- [ ] document that substitution and verify retention
- [ ] define secret replication/recovery and KMS key access
- [ ] define Amazon MQ topology/message recovery limits
- [ ] set lifecycle retention and cross-region copy only if budget supports
- [ ] specify RPO/RTO separately for DB, secrets, object artifacts and broker
- [ ] conduct restore drill into isolated recovery resources and run application integrity checks
- [ ] schedule recurring drill.

## Acceptance criteria
- [ ] Restore drill meets documented RPO/RTO for RDS and recovers test secrets
- [ ] restored app passes user-flow smoke
- [ ] broker recovery limitations are explicit and tested
- [ ] backups encrypted and lifecycle-managed
- [ ] recovery account/role access audited
- [ ] restore costs and teardown are captured

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
