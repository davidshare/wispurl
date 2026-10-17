---
id: cloud-014
title: Terraform AWS infrastructure modules and environment separation
type: feat
feature: 9. Infrastructure as Code
status: not_started
depends_on: [cloud-001]
checklist_sections: 9. Infrastructure as Code; 4. Cloud CI/CD
---

# Terraform AWS infrastructure modules and environment separation

## Goal
Make every AWS resource in this project reproducible and reviewable through Terraform.

## Implementation subtasks
- [ ] Organize reusable modules and separate dev/staging/production-like variable/state boundaries
- [ ] pin Terraform and provider versions
- [ ] run fmt, validate, plan, tfsec and Checkov in PR
- [ ] require reviewed plan before apply
- [ ] define IAM least privilege, tagging, dependency ordering and teardown
- [ ] prohibit plaintext secret inputs/outputs
- [ ] keep state in encrypted S3 with DynamoDB lock from foundation issue
- [ ] inventory configuration tasks and keep Ansible out unless a task is not owned by Terraform or managed AWS services.

## Acceptance criteria
- [ ] Clean checkout initializes using remote backend
- [ ] formatting/validation and both security scans pass
- [ ] plan contains no secret values
- [ ] environment state cannot overlap
- [ ] a reviewed plan creates and destroys a minimal demo slice
- [ ] policy blocks public data stores and wildcard IAM
- [ ] no resource is co-managed by Terraform and Ansible

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
