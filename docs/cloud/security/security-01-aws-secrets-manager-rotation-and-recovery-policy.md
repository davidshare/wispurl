---
id: cloud-003
title: AWS Secrets Manager, rotation, and recovery policy
type: feat
feature: 2. Secrets Management
status: not_started
depends_on: [cloud-001]
checklist_sections: 2. Secrets Management; 8. Backups and Disaster Recovery
---

# AWS Secrets Manager, rotation, and recovery policy

## Goal
Replace local Vault-only cloud assumptions with AWS Secrets Manager while retaining a production-style secret lifecycle.

## Implementation subtasks
- [ ] Create one secret per service/environment with clear ownership and rotation metadata
- [ ] encrypt with KMS customer-managed key where cost allows
- [ ] configure EKS identity access via IRSA and External Secrets Operator in its own dependent issue
- [ ] enable CloudTrail data/access events and alerts for reads
- [ ] use Secrets Manager rotation for RDS credentials and document rotation owner/process for non-AWS API keys
- [ ] define replication/recovery instead of Vault Raft snapshot/auto-unseal
- [ ] implement break-glass access via separate MFA-protected role with audit
- [ ] ensure secret values never enter Terraform state, plans, image layers or logs.

## Acceptance criteria
- [ ] A pod role reads only its assigned secret
- [ ] cross-service read is denied
- [ ] RDS rotation changes working credentials and application reconnect is verified
- [ ] CloudTrail shows principal, secret ARN and time for allow/deny
- [ ] break-glass procedure is exercised in a non-production secret
- [ ] restore/replication drill recovers a test secret
- [ ] cost and unsupported API-key auto-rotation limitations are documented

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
