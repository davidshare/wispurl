---
id: local-029
title: RabbitMQ dead-lettering and duplicate-delivery safety
type: feat
feature: 7. Reliability and SRE
status: not_started
depends_on: [local-028]
checklist_sections: 7. Reliability and SRE; 8. Backups and Disaster Recovery
---

# RabbitMQ dead-lettering and duplicate-delivery safety

## Goal
Make asynchronous analytics/notification processing recoverable when consumers fail or messages are delivered more than once.

## Implementation subtasks
- [ ] Inventory exchanges, queues, routing keys and consumers
- [ ] configure durable DLX/DLQ and dead-letter routing for poison messages
- [ ] define max delivery/requeue policy and queue TTL/length limits
- [ ] make analytics consumer idempotent using event identifiers
- [ ] document replay procedure that does not bypass validation
- [ ] export/import definitions for local recovery.

## Acceptance criteria
- [ ] Malformed message reaches DLQ after bounded retries
- [ ] valid message is acknowledged once
- [ ] duplicated delivery creates one logical result
- [ ] DLQ message can be inspected and safely replayed
- [ ] exported RabbitMQ definitions restore exchanges, bindings, policies and queues in a clean broker

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
