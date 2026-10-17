---
id: cloud-028
title: Dependabot dependency and workflow update automation
type: feat
feature: 5. Container Security
status: not_started
depends_on: [cloud-011]
checklist_sections: 5. Container Security; 4. Cloud CI/CD
---

# Dependabot dependency and workflow update automation

## Goal
Automate reviewable dependency and base-image updates for the GitHub-hosted project.

## Implementation subtasks
- [ ] Enable Dependabot for all uv/Python manifests and lockfiles, frontend npm lockfile, GitHub Actions references, Docker base images, Helm charts and Terraform providers
- [ ] group safe patch updates
- [ ] require CI and security scans on update PRs
- [ ] define handling for critical advisories and unsupported upgrades
- [ ] do not auto-merge major/runtime or infrastructure changes.

## Acceptance criteria
- [ ] A scheduled update PR is produced for each supported ecosystem
- [ ] every update runs all required checks
- [ ] a deliberately vulnerable test dependency produces an actionable alert
- [ ] no update merges without protected checks
- [ ] ownership and review cadence are documented

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
