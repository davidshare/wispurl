---
id: cloud-011
title: GitHub Actions AWS delivery pipeline with OIDC
type: feat
feature: 4. Cloud CI/CD
status: not_started
depends_on: [cloud-001]
checklist_sections: 4. Cloud CI/CD
---

# GitHub Actions AWS delivery pipeline with OIDC

## Goal
Implement cloud CI/CD in GitHub Actions, matching the project’s GitHub remote and avoiding long-lived AWS access keys.

## Implementation subtasks
- [ ] Use GitHub OIDC to assume separate read-only plan, image-publish, and deploy roles
- [ ] run on pull requests and protected default-branch/release events
- [ ] require approvals before staging/production-like deploy
- [ ] order lint, type, tests, Gitleaks, SAST, dependency scan, Checkov, image build, Trivy, Syft, Cosign, ECR push, Terraform plan/apply, ArgoCD GitOps update, smoke test and rollback
- [ ] constrain workflow permissions, environments, branch protection and artifact retention
- [ ] publish only SHA/digest-addressed images.

## Acceptance criteria
- [ ] Fork PR cannot obtain AWS credentials
- [ ] untrusted PR runs no apply/publish
- [ ] OIDC session is short-lived and role-scoped
- [ ] any required gate failure blocks release
- [ ] manual environment approval is recorded
- [ ] deployed image digest maps to commit/SBOM/signature
- [ ] rollback executes on failed smoke test or blocks promotion with a documented operator action

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
