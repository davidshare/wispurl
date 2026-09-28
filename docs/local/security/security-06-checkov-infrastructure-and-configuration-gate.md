---
id: local-013
title: Checkov infrastructure and configuration gate
type: feat
feature: 4. Local CI/CD Pipeline
status: not_started
depends_on: [local-010]
checklist_sections: 4. Local CI/CD Pipeline
---

# Checkov infrastructure and configuration gate

## Goal
Scan the repository’s infrastructure and deployment configuration with Checkov so insecure Compose, Kubernetes, Helm, and future Terraform changes are caught before merge.

## Implementation subtasks
- [ ] Scan docker-compose.yml, compose.observability.yaml, all Kubernetes manifests/Helm chart files, and Terraform paths when introduced
- [ ] set a failing severity threshold
- [ ] maintain narrowly scoped skip annotations with reason and issue reference
- [ ] publish a readable report
- [ ] distinguish unsupported checks from passed checks.

## Acceptance criteria
- [ ] A controlled insecure fixture for privileged container/public secret exposure fails
- [ ] current repository scan runs in CI
- [ ] no blanket path or framework exclusion exists
- [ ] each skip has rationale and reference
- [ ] scanner errors fail the job

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
