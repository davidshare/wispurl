---
id: LOC-7.11
title: "Chaos test: message duplication simulated and verified"
category: "7. Reliability and SRE (Local Validation)"
status: todo
related:
  - docs/local/sre/sre-03-local-failure-injection-and-chaos-validation.md
  - docs/local/app/app-05-rabbitmq-dead-lettering-and-duplicate-delivery-safety.md
---

# Chaos test: message duplication simulated and verified

## What
Duplicate message delivery doesn't create duplicate side effects.

## Current state
None (depends on idempotency work).

## Subtasks
- [ ] Republish the same click/milestone message N times (script or management API)
- [ ] Verify one `click_event` row and one notification

## Acceptance criteria
- [ ] N duplicates → exactly one effect
