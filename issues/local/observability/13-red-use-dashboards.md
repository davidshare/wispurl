---
id: LOC-6.13
title: "Dashboards covering RED metrics (Rate, Errors, Duration) and USE metrics (Utilization, Saturation, Errors)"
category: "6. Observability (Local Stack)"
status: partial
related:
  - docs/local/observability/obs-04-grafana-dashboards-and-data-sources.md
---

# Dashboards covering RED metrics (Rate, Errors, Duration) and USE metrics (Utilization, Saturation, Errors)

## What
Dashboards show RED (rate, errors, duration) per service and USE (utilisation, saturation, errors) per resource.

## Current state
None (no Grafana).

## Subtasks
- [x] Service overview: request rate, 5xx ratio, p50/p95/p99 per service
- [x] USE: CPU, memory and network per container; host resources
- [x] Dependency dashboards: Postgres, Redis, RabbitMQ (queue depth, DLQ)
- [x] Linked log and trace panels
- [x] Dashboards stored as JSON in git and provisioned

## Acceptance criteria
- [ ] A load test is visible on the RED dashboard and container saturation on the USE dashboard
