---
id: LOC-4.03
title: "Pipeline stage: static type checking"
category: "4. Local CI/CD Pipeline (GitLab CI or Jenkins)"
status: todo
related:
  - docs/local/cicd/cicd-00-github-actions-continuous-integration-pipeline.md
---

# Pipeline stage: static type checking

## What
Pipeline stage running static type checks.

## Current state
README documents `uv run mypy --strict .` per service, but it isn't automated.

## Subtasks
- [ ] `mypy --strict` for each Python service and shared library
- [ ] `tsc --noEmit` for the frontend

## Acceptance criteria
- [ ] A type error fails the stage
