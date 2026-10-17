---
id: LOC-4.06
title: "Pipeline stage: SAST with Semgrep and Bandit (Python)"
category: "4. Local CI/CD Pipeline (GitLab CI or Jenkins)"
status: todo
related:
  - docs/local/security/security-05-static-analysis-and-dependency-vulnerability-gates.md
---

# Pipeline stage: SAST with Semgrep and Bandit (Python)

## What
Static application security testing with Semgrep and Bandit.

## Current state
None.

## Subtasks
- [ ] `semgrep` with `p/python`, `p/owasp-top-ten`, `p/typescript`
- [ ] `bandit -r app -ll` per Python service
- [ ] Fail on high severity, and keep a reviewed baseline for accepted findings
- [ ] Upload SARIF reports

## Acceptance criteria
- [ ] A planted vulnerable pattern (e.g. `subprocess` with `shell=True`) fails the stage
