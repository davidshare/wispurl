---
id: cloud-033
title: Terraform and Ansible ownership boundary
type: feat
feature: 9. Infrastructure as Code
status: not_started
depends_on: [cloud-001]
checklist_sections: 9. Infrastructure as Code
---

# Terraform and Ansible ownership boundary

## Goal
Define whether Ansible is needed without allowing two tools to manage the same AWS resource.

## Implementation subtasks
- [ ] Use Terraform as source of truth for AWS resources, IAM, EKS and managed-service configuration
- [ ] inventory tasks outside Terraform ownership
- [ ] add Ansible only for an identified host/configuration task and pin its collections
- [ ] otherwise document why managed EKS/AWS services leave no Ansible responsibility.

## Acceptance criteria
- [ ] Every infrastructure/configuration task has one owner tool
- [ ] Terraform and Ansible do not co-manage a resource
- [ ] any Ansible role is idempotent across two runs
- [ ] if none is required, record a justified not-applicable decision in the checklist

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
