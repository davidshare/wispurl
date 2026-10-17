---
id: cloud-012
title: Cloud Gitleaks gate and secret incident workflow
type: feat
feature: 2. Secrets Management
status: not_started
depends_on: [cloud-011]
checklist_sections: 2. Secrets Management; 4. Cloud CI/CD
---

# Cloud Gitleaks gate and secret incident workflow

## Goal
Enforce Gitleaks as a required blocking check on every cloud-bound change, independent of the local pre-commit hook.

## Implementation subtasks
- [ ] Scan current tree and commit history with pinned version and shared project rules
- [ ] fail on findings and tool errors
- [ ] keep baseline narrow and reviewed
- [ ] create restricted short-lived failure artifact
- [ ] document revoke/rotate, remove-from-history, and incident reporting steps
- [ ] configure branch protection to require the result.

## Acceptance criteria
- [ ] Synthetic canary finding blocks PR and merge
- [ ] tool outage fails job
- [ ] no broad allowlist masks Terraform, YAML or CI paths
- [ ] job result is a required branch-protection check
- [ ] response runbook identifies rotation actions without reproducing leaked value

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
