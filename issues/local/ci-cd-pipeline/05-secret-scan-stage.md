---
id: LOC-4.05
title: "Pipeline stage: secret scanning (Gitleaks) — blocking"
category: "4. Local CI/CD Pipeline (GitLab CI or Jenkins)"
status: todo
related:
  - docs/local/security/security-04-blocking-gitleaks-ci-gate.md
---

# Pipeline stage: secret scanning (Gitleaks) — **blocking**

## What
Blocking Gitleaks stage in the local pipeline.

## Current state
Gitleaks runs in GitHub Actions only (see Secrets → blocking CI).

## Subtasks
- [ ] Run gitleaks with `.gitleaks.toml` (full history on the default branch, diff on PRs)
- [ ] Fail the pipeline on any finding
- [ ] Upload the JSON/SARIF report as an artifact

## Acceptance criteria
- [ ] A planted fake secret fails the pipeline
