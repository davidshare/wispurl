---
id: LOC-3.02
title: "Integration tests covering service interactions"
category: "3. Testing"
status: todo
related:
  - docs/local/app/app-03-local-application-test-suite-and-coverage.md
---

# Integration tests covering service interactions

## What
Tests exercise real interactions between services and their dependencies.

## Current state
None.

## Subtasks
- [ ] Create an integration suite that runs against the Compose stack
- [ ] Cover signup → login → create link → redirect → stats through the gateway
- [ ] Reset state between runs (fresh DBs or transactional fixtures)
- [ ] Add `make test-integration`

## Acceptance criteria
- [ ] The core user flow passes end to end against a fresh stack
