---
id: local-010
title: GitHub Actions continuous integration pipeline
type: feat
feature: 4. Local CI/CD Pipeline
status: not_started
depends_on: []
checklist_sections: 4. Local CI/CD Pipeline
---

# GitHub Actions continuous integration pipeline

## Goal
Create the repository CI pipeline in GitHub Actions because the project remote is GitHub, with the same workflow runnable locally through act for portfolio demonstration.

## Implementation subtasks
- [ ] Run on pull requests and pushes to the default branch
- [ ] use ruff check and ruff format check plus mypy strict for every Python project
- [ ] run frontend npm lint and build scripts
- [ ] provide separate named jobs for tests and coverage, Gitleaks, Semgrep/Bandit, pip-audit/npm audit, Checkov, image build, Trivy, Syft SBOM, local Registry:2 publication, Kind deployment, ArgoCD sync from a GitOps revision, post-deploy smoke tests, and rollback on unhealthy deployment
- [ ] require all quality/security jobs before merge
- [ ] tag images with commit SHA
- [ ] ensure forks do not receive secrets
- [ ] define artifact retention and cache keys
- [ ] use least privilege workflow permissions
- [ ] local act mode must skip only AWS-authenticated operations with an explicit reason.

## Acceptance criteria
- [ ] A pull request runs every non-deployment gate
- [ ] any failing required job makes the workflow red
- [ ] Python lint, formatting, type checks and frontend lint/build execute for all applicable projects
- [ ] no secrets are available to untrusted fork runs
- [ ] rerun is deterministic
- [ ] artifacts identify commit SHA
- [ ] local act run executes lint/test/scans without AWS credentials
- [ ] Kind deployment is promoted through ArgoCD and smoke failure prevents promotion or restores previous Git revision
- [ ] workflow and required-check names are documented

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
