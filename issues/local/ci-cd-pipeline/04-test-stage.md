---
id: LOC-4.04
title: "Pipeline stage: unit and integration test execution"
category: "4. Local CI/CD Pipeline (GitLab CI or Jenkins)"
status: todo
related:
  - docs/local/app/app-03-local-application-test-suite-and-coverage.md
---

# Pipeline stage: unit and integration test execution

## What
Pipeline stage running unit and integration tests against real dependencies.

## Current state
No tests exist yet (see Testing).

## Subtasks
- [ ] Run unit tests per service
- [ ] Run integration tests with Postgres, Redis and RabbitMQ service containers
- [ ] Publish JUnit and coverage artifacts

## Acceptance criteria
- [ ] A failing test fails the pipeline, and reports are attached
