---
id: LOC-4.02
title: "Pipeline stage: linting and code formatting"
category: "4. Local CI/CD Pipeline (GitLab CI or Jenkins)"
status: todo
related:
  - docs/local/cicd/cicd-00-github-actions-continuous-integration-pipeline.md
---

# Pipeline stage: linting and code formatting

## What
Pipeline stage that fails on lint or formatting violations.

## Current state
Services have ruff configured but nothing runs it automatically.

## Subtasks
- [ ] `ruff check` and `ruff format --check` for each Python service (matrix)
- [ ] `npm run lint` (ESLint) for the frontend
- [ ] `hadolint` for Dockerfiles, `shellcheck` for scripts, `yamllint` for YAML

## Acceptance criteria
- [ ] A formatting violation fails the stage
