---
id: LOC-4.01
title: "Local GitLab CI runner registered, or local Jenkins instance/agent configured"
category: "4. Local CI/CD Pipeline (GitLab CI or Jenkins)"
status: todo
related:
  - docs/local/cicd/cicd-00-github-actions-continuous-integration-pipeline.md
---

# Local GitLab CI runner registered, or local Jenkins instance/agent configured

## What
A CI engine and runner execute the pipeline locally, with the pipeline definition versioned in the repo.

## Current state
Only two GitHub Actions secret-scan workflows exist. The checklist assumes GitLab CI or Jenkins; `docs/local` plans GitHub Actions (local-010).

## Subtasks
- [ ] Decide the engine (local GitLab CE + runner, Jenkins, or GitHub Actions with a self-hosted runner/`act`) and record the decision
- [ ] Stand up and register the runner with a Docker executor
- [ ] Commit the pipeline definition (`.gitlab-ci.yml`, `Jenkinsfile`, or `.github/workflows/ci.yml`)
- [ ] Store CI credentials (registry, ArgoCD token) in the CI secret store, never in the repo
- [ ] Run independent jobs in parallel and cache uv/npm downloads

## Acceptance criteria
- [ ] A push triggers the pipeline on the local runner and results are visible

## Notes
- Pipeline shape: lint → type check → test → secret scan → SAST → dependency scan → IaC scan → build → image scan → SBOM → push → ArgoCD sync → smoke test → rollback if unhealthy.
