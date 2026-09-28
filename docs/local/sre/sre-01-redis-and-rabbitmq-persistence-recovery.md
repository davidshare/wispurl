---
id: local-032
title: Redis and RabbitMQ persistence/recovery
type: feat
feature: 8. Backups and Disaster Recovery
status: not_started
depends_on: []
checklist_sections: 8. Backups and Disaster Recovery
---

# Redis and RabbitMQ persistence/recovery

## Goal
Define and verify local persistence and recovery for Redis and RabbitMQ separately from PostgreSQL.

## Implementation subtasks
- [ ] Choose Redis RDB or AOF based on the project’s cache/rate-limit semantics
- [ ] configure persistence and volume mount accordingly
- [ ] document whether cache loss is acceptable and rate-limit impact
- [ ] define RabbitMQ persistence, definitions export, message durability and recovery behavior
- [ ] run broker import drill after clean volume creation.

## Acceptance criteria
- [ ] Redis persistence choice is documented and survives the defined restart scenario
- [ ] data that is intentionally cache-only is identified
- [ ] RabbitMQ topology imports successfully
- [ ] durable messages survive container restart
- [ ] recovery runbook describes what is and is not restored

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
