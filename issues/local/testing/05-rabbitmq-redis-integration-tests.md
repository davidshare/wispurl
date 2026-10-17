---
id: LOC-3.05
title: "RabbitMQ and Redis integration tests using local containerized instances"
category: "3. Testing"
status: todo
related:
  - docs/local/app/app-05-rabbitmq-dead-lettering-and-duplicate-delivery-safety.md
---

# RabbitMQ and Redis integration tests using local containerized instances

## What
Messaging and rate-limiting behaviour is tested against real containerised RabbitMQ and Redis.

## Current state
None.

## Subtasks
- [ ] Use testcontainers or the Compose stack for RabbitMQ and Redis
- [ ] Test publish → consume → ack, retry with backoff and dead-lettering after max attempts
- [ ] Test malformed messages go straight to `events.dlq`
- [ ] Test the rate-limit window, reset and `RATE_LIMITER_FAIL_OPEN` behaviour when Redis is down

## Acceptance criteria
- [ ] The suite passes against real brokers, and the DLQ path is asserted
