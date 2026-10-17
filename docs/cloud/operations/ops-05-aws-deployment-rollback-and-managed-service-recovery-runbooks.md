---
id: cloud-034
title: AWS deployment, rollback, and managed-service recovery runbooks
type: feat
feature: 12. Operations and Incident Response
status: not_started
depends_on: [cloud-003, cloud-006, cloud-008, cloud-015]
checklist_sections: 12. Operations and Incident Response
---

# AWS deployment, rollback, and managed-service recovery runbooks

## Goal
Provide operator-ready procedures for every cloud recovery surface without referring to Vault, which is not part of the selected cloud design.

## Implementation subtasks
- [ ] Write step-by-step deploy and rollback runbooks using GitHub Actions and ArgoCD
- [ ] write RDS point-in-time restore and validation procedure
- [ ] write AWS Secrets Manager access/rotation/recovery procedure
- [ ] write Amazon MQ topology and DLQ recovery procedure
- [ ] identify required IAM role, approval, expected output, destructive actions, recovery time estimate and cleanup for each
- [ ] have a second person follow the procedures in a disposable environment.

## Acceptance criteria
- [ ] Each runbook contains prerequisites, exact AWS/EKS resource identifiers to locate, actions, validation and rollback
- [ ] a second operator completes a deployment rollback, isolated RDS restore, test-secret recovery and broker topology recovery
- [ ] no runbook requires root credentials or exposes secret values
- [ ] measured recovery duration and limitations are recorded

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
