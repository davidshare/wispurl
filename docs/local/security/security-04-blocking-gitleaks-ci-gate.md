---
id: local-011
title: Blocking Gitleaks CI gate
type: feat
feature: 4. Local CI/CD Pipeline
status: not_started
depends_on: [local-010]
checklist_sections: 4. Local CI/CD Pipeline; 2. Secrets Management
---

# Blocking Gitleaks CI gate

## Goal
Add a separate blocking secret scan stage to GitHub Actions, distinct from local pre-commit.

## Implementation subtasks
- [ ] Run pinned Gitleaks against the full checked-out repository history and current tracked content on pull requests and default-branch pushes
- [ ] use the repository config and explicit baseline only where justified
- [ ] do not convert nonzero results to success
- [ ] upload a redacted report only on failure with restricted retention
- [ ] document new-secret response and history remediation.

## Acceptance criteria
- [ ] A synthetic secret introduced in a test branch fails the job
- [ ] a clean branch passes
- [ ] scanner installation/runtime failures fail closed
- [ ] findings are not printed with unnecessary secret context or retained in public artifacts
- [ ] branch protection can mark the job required

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
