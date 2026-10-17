---
id: LOC-7.06
title: "Dead-letter queues configured for failed message processing"
category: "7. Reliability and SRE (Local Validation)"
status: done
related:
  - docs/local/app/app-05-rabbitmq-dead-lettering-and-duplicate-delivery-safety.md
---

# Dead-letter queues configured for failed message processing

## What
Messages that can't be processed land in a durable dead-letter queue instead of looping or being dropped.

## Current state
Shared messaging declares durable `events.dlq`; malformed messages are dead-lettered immediately and others after max attempts.

## Subtasks
- [x] Durable `events.dlq` declared by every producer/consumer
- [x] Malformed messages dead-lettered without retry
- [x] Exhausted retries dead-lettered

## Acceptance criteria
- [x] A poison message ends up in `events.dlq` and processing continues

## Notes
- Alert on DLQ depth ([Alertmanager](../observability/12-alertmanager.md)) and document replay ([RabbitMQ runbook](../operations-incident-response/06-rabbitmq-recovery-runbook.md)).

## References
- [shortener-service/shared/messaging.py](../../../shortener-service/shared/messaging.py)
