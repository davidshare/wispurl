---
id: cloud-001
title: AWS account foundation, Terraform state, and cost guardrails
type: feat
feature: 9. Infrastructure as Code
status: not_started
depends_on: []
checklist_sections: 9. Infrastructure as Code; 13. Cost and Capacity
---

# AWS account foundation, Terraform state, and cost guardrails

## Goal
Create the safe foundation for all cloud work in a dedicated AWS portfolio account and region.

## Implementation subtasks
- [ ] Choose a single AWS region
- [ ] require MFA and avoid root access for routine work
- [ ] configure Terraform S3 remote state with encryption/versioning and DynamoDB locking
- [ ] separate dev/staging/production state and IAM roles
- [ ] enable AWS Budgets alerts at 50/80/100 percent
- [ ] tag every resource with owner, environment, project and expiry
- [ ] define a teardown procedure and identify intentionally persistent resources.

## Acceptance criteria
- [ ] Terraform plan is reproducible from a clean checkout
- [ ] state bucket denies public access and logs access
- [ ] locking prevents concurrent state mutation
- [ ] no secret is stored in state
- [ ] budget alerts reach a verified mailbox
- [ ] all provisioned resources have tags and documented monthly estimate

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
