---
id: LOC-8.06
title: "RabbitMQ definitions export/import drill"
category: "8. Backups and Disaster Recovery (Local)"
status: todo
related:
  - docs/local/sre/sre-01-redis-and-rabbitmq-persistence-recovery.md
---

# RabbitMQ definitions export/import drill

## What
RabbitMQ topology (exchanges, queues, bindings, users, policies) can be exported and restored.

## Current state
Data persists in a volume, but no definitions backup.

## Subtasks
- [ ] Export with `rabbitmqctl export_definitions` (or the management API) to `backups/rabbitmq/`
- [ ] Import into a fresh broker and verify queues, including `events.dlq`
- [ ] Optionally load definitions at startup (`load_definitions`)
- [ ] Note that messages are not included and what that means

## Acceptance criteria
- [ ] A fresh broker restored from definitions serves the app
