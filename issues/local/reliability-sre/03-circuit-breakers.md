---
id: LOC-7.03
title: "Circuit breakers added for external dependencies"
category: "7. Reliability and SRE (Local Validation)"
status: todo
related:
  - docs/local/app/app-04-resilience-controls-for-outbound-calls-and-message-processing.md
---

# Circuit breakers added for external dependencies

## What
Calls to flaky dependencies trip a circuit breaker so failures are fast and dependencies can recover.

## Current state
None.

## Subtasks
- [ ] Pick a library (e.g. `aiobreaker`/`purgatory`) or a small shared implementation
- [ ] Wrap shortener → analytics, shortener → rate-limiter and gateway → upstreams
- [ ] Configure failure threshold, open duration and half-open probe
- [ ] Export breaker state as a metric and log state changes
- [ ] Tests for open/half-open/closed transitions

## Acceptance criteria
- [ ] With analytics down, shortener stops calling it after the threshold and resumes after recovery
