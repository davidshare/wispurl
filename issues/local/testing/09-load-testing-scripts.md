---
id: LOC-3.09
title: "Local load testing scripts using k6 or Locust"
category: "3. Testing"
status: todo
related:
  - docs/local/sre/sre-04-local-load-and-capacity-baseline-plus-retention-limits.md
---

# Local load testing scripts using k6 or Locust

## What
Repeatable load tests exercise the main paths with clear pass/fail thresholds.

## Current state
None.

## Subtasks
- [ ] Create k6 (or Locust) scripts under `loadtest/`: redirect hot path, create link, login
- [ ] Define thresholds (p95 latency, error rate)
- [ ] Add `make loadtest` and store results
- [ ] Feed results into the capacity baseline

## Acceptance criteria
- [ ] Load test runs locally and reports threshold pass/fail
