---
id: LOC-7.04
title: "Idempotency keys implemented for critical operations (payments, link creation)"
category: "7. Reliability and SRE (Local Validation)"
status: todo
related:
  - docs/local/app/app-05-rabbitmq-dead-lettering-and-duplicate-delivery-safety.md
---

# Idempotency keys implemented for critical operations (payments, link creation)

## What
Critical writes can be safely retried: link creation honours an idempotency key and event consumers deduplicate.

## Current state
None. README notes click-event processing isn't idempotent against duplicate delivery.

## Subtasks
- [ ] Accept an `Idempotency-Key` header on `POST /links`, storing key + user + request hash + response with a TTL
- [ ] Return the stored response for a repeated key, and 409 for the same key with a different body
- [ ] Add a unique `event_id` to click events, with an `ON CONFLICT DO NOTHING` insert
- [ ] Deduplicate milestone notifications
- [ ] Tests for duplicate requests and duplicate messages

## Acceptance criteria
- [ ] Replaying a create request or a click message produces no duplicate rows
