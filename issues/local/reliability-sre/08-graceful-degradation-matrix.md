---
id: LOC-7.08
title: "Graceful degradation / fail-open / fail-closed behaviors documented and tested"
category: "7. Reliability and SRE (Local Validation)"
status: partial
related:
  - docs/local/app/app-04-resilience-controls-for-outbound-calls-and-message-processing.md
---

# Graceful degradation / fail-open / fail-closed behaviors documented and tested

## What
For each dependency, the intended behaviour on failure (fail-open, fail-closed, degraded) is documented and tested.

## Current state
Rate limiting is fail-open (configurable) and analytics on redirect is fire-and-forget, but there is no written matrix and no tests.

## Subtasks
- [x] Rate-limiter fail-open setting
- [x] Analytics publish on redirect does not block the redirect
- [ ] Write a matrix: Postgres, Redis, RabbitMQ, Vault, analytics, rate limiter, qr → behaviour + rationale
- [ ] Add a test per matrix row (links to failure tests)

## Acceptance criteria
- [ ] The matrix exists and every row has a passing test or chaos result
