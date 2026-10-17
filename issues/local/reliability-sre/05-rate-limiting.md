---
id: LOC-7.05
title: "Rate limiting logic implemented and tested locally"
category: "7. Reliability and SRE (Local Validation)"
status: partial
related:
  - docs/local/app/app-04-resilience-controls-for-outbound-calls-and-message-processing.md
---

# Rate limiting logic implemented and tested locally

## What
Rate limits protect expensive and abuse-prone endpoints and are verified by tests.

## Current state
`rate-limiter-service` implements a Redis fixed-window limit for link creation; shortener calls it with a timeout and a fail-open flag. There's no limit on auth/redirect paths and no tests.

## Subtasks
- [x] Rate-limiter service backed by Redis with a configurable window/limit
- [x] Shortener enforces the limit with a timeout and `RATE_LIMITER_FAIL_OPEN`
- [ ] Add per-IP limits on login/signup (brute force) and redirects at the gateway
- [ ] Return 429 with `Retry-After`
- [ ] Unit and integration tests: limit reached, window reset, fail-open/closed

## Acceptance criteria
- [ ] Exceeding the limit returns 429 in tests, and fail-open behaviour is asserted
