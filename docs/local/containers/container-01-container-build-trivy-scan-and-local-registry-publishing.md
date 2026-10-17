---
id: local-014
title: Container build, Trivy scan, and local registry publishing
type: feat
feature: 4. Local CI/CD Pipeline
status: not_started
depends_on: [local-010]
checklist_sections: 4. Local CI/CD Pipeline; Multi-stage application images and runtime hardening
---

# Container build, Trivy scan, and local registry publishing

## Goal
Build, scan, tag, and optionally publish all project service images as traceable artifacts.

## Implementation subtasks
- [ ] Build all application service images plus Vault
- [ ] tag with full Git commit SHA
- [ ] scan every image with Trivy including OS packages and language dependencies
- [ ] fail on fixable Critical and High findings under a documented exception policy
- [ ] produce per-image reports
- [ ] push only verified images to a local Registry service in the local pipeline and to ECR in the cloud pipeline
- [ ] never publish from untrusted pull-request contexts.

## Acceptance criteria
- [ ] All images build from a clean checkout
- [ ] each has the commit-SHA tag
- [ ] a vulnerable test image fails the configured threshold
- [ ] no image uses latest
- [ ] local registry contains only successful default-branch images
- [ ] scan reports map to image digest and commit

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
