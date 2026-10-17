---
id: LOC-3.08
title: "Failure and timeout tests validating application resilience"
category: "3. Testing"
status: todo
related:
  - docs/local/app/app-04-resilience-controls-for-outbound-calls-and-message-processing.md
---

# Failure and timeout tests validating application resilience

## What
Tests prove the app behaves correctly when dependencies are slow or down.

## Current state
Timeouts and fail-open logic exist in code but are untested.

## Subtasks
- [ ] Analytics slow/down → redirect still succeeds
- [ ] Rate limiter down → link creation follows the fail-open setting
- [ ] Upstream timeout → gateway returns 504
- [ ] Vault unreachable at startup → service fails fast with a clear error
- [ ] RabbitMQ down → publish failure handled without crashing the request
- [ ] Use respx for unit-level and Toxiproxy for integration-level faults

## Acceptance criteria
- [ ] Each documented degradation behaviour has a passing test
