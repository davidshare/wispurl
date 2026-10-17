---
id: LOC-6.12
title: "Local Alertmanager configured with basic routing rules"
category: "6. Observability (Local Stack)"
status: partial
related:
  - docs/local/observability/obs-05-local-alertmanager-rules-and-runbook-links.md
---

# Local Alertmanager configured with basic routing rules

## What
Alertmanager receives Prometheus alerts and routes them by severity.

## Current state
None.

## Subtasks
- [x] Add a pinned Alertmanager service on loopback
- [x] Configure Prometheus `alerting` and `rule_files`
- [x] Rules: target down, 5xx rate, p95 latency, DLQ depth > 0, queue backlog, Postgres connections near max, Redis down, disk usage
- [ ] Vault sealed alert (needs Vault's telemetry endpoint scraped first)
- [x] Route by severity to a local receiver (webhook, Mailpit or log), with inhibition rules
- [x] Validate with `promtool check rules` and `amtool check-config`

## Acceptance criteria
- [x] Stopping a service fires an alert that reaches the receiver, and it resolves on recovery
