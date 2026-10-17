---
id: LOC-7.02
title: "Retries with exponential backoff implemented and tested"
category: "7. Reliability and SRE (Local Validation)"
status: partial
related:
  - docs/local/app/app-04-resilience-controls-for-outbound-calls-and-message-processing.md
---

# Retries with exponential backoff implemented and tested

## What
Transient failures are retried with capped exponential backoff + jitter, only for idempotent operations, and the behaviour is tested.

## Current state
Message processing retries with capped exponential backoff (`x-attempt`) before dead-lettering; broker/consumer loops reconnect with backoff. No retries on outbound HTTP or the Vault login; no tests.

## Subtasks
- [x] Message retry with capped exponential backoff and attempt counter
- [x] Reconnect loops with backoff for consumers and cleanup
- [ ] Add bounded retries with jitter (e.g. tenacity) for Vault login at startup and idempotent GETs
- [ ] Never retry non-idempotent POSTs without an idempotency key
- [ ] Tests that assert retry counts and backoff timing

## Acceptance criteria
- [ ] Tests show N retries then success or DLQ, and no retry storm under a dependency outage
