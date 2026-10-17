---
id: LOC-4.07
title: "Pipeline stage: dependency vulnerability scanning (pip-audit, npm audit, etc.)"
category: "4. Local CI/CD Pipeline (GitLab CI or Jenkins)"
status: todo
related:
  - docs/local/security/security-05-static-analysis-and-dependency-vulnerability-gates.md
---

# Pipeline stage: dependency vulnerability scanning (pip-audit, npm audit, etc.)

## What
Known-vulnerable dependencies fail the pipeline.

## Current state
None.

## Subtasks
- [ ] `pip-audit` per Python service (from `uv export --frozen`)
- [ ] `npm audit --audit-level=high` for the frontend
- [ ] Allowlist file with justification and expiry for accepted CVEs

## Acceptance criteria
- [ ] A dependency with a known high CVE fails the stage
