---
id: LOC-6.12
title: "Local Alertmanager configured with basic routing rules"
category: "6. Observability (Local Stack)"
status: todo
related:
  - docs/local/observability/obs-05-local-alertmanager-rules-and-runbook-links.md
---

# Local Alertmanager configured with basic routing rules

## What
Alertmanager receives Prometheus alerts and routes them by severity.

## Current state
None.

## Subtasks
- [ ] Add a pinned Alertmanager service on loopback
- [ ] Configure Prometheus `alerting` and `rule_files`
- [ ] Rules: target down, 5xx rate, p95 latency, DLQ depth > 0, queue backlog, Postgres connections near max, Redis down, Vault sealed, disk usage
- [ ] Route by severity to a local receiver (webhook, Mailpit or log), with inhibition rules
- [ ] Validate with `promtool check rules` and `amtool check-config`

## Acceptance criteria
- [ ] Stopping a service fires an alert that reaches the receiver, and it resolves on recovery
