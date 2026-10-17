---
id: LOC-3.07
title: "Test coverage reporting integrated into local CI output"
category: "3. Testing"
status: todo
related:
  - docs/local/app/app-03-local-application-test-suite-and-coverage.md
---

# Test coverage reporting integrated into local CI output

## What
Test coverage is measured and visible in CI output, with a minimum threshold.

## Current state
None.

## Subtasks
- [ ] Add `pytest-cov` and produce terminal + XML reports per service
- [ ] Set an initial threshold (e.g. 70%) with `--cov-fail-under`
- [ ] Publish coverage artifacts from the pipeline

## Acceptance criteria
- [ ] CI shows per-service coverage and fails below the threshold
