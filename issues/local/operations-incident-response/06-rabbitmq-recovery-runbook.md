---
id: LOC-11.06
title: "Local RabbitMQ recovery runbook created"
category: "11. Operations and Incident Response (Local)"
status: todo
related:
  - docs/local/sre/sre-05-postgresql-vault-and-rabbitmq-recovery-runbooks.md
---

# Local RabbitMQ recovery runbook created

## What
Runbook for recovering RabbitMQ.

## Current state
None.

## Subtasks
- [ ] Scenarios: broker down, queue backlog, DLQ growth, lost definitions, credential reset
- [ ] DLQ inspection and replay procedure
- [ ] Definitions restore and consumer restart order

## Acceptance criteria
- [ ] DLQ replay and definitions restore performed from the runbook
