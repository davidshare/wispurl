---
id: local-021
title: Grafana dashboards and data sources
type: feat
feature: 6. Observability
status: not_started
depends_on: [local-020]
checklist_sections: 6. Observability
---

# Grafana dashboards and data sources

## Goal
Add the missing local Grafana service and provision usable dashboards/data sources rather than leaving metrics, logs, and traces without a UI.

## Implementation subtasks
- [ ] Pin Grafana image
- [ ] configure Prometheus, Loki, and Tempo data sources by Compose service DNS
- [ ] persist dashboard provisioning
- [ ] create service overview and per-service dashboards with RED rate/error/duration panels plus USE utilization/saturation/error panels
- [ ] include PostgreSQL pool/health, Redis, RabbitMQ queue/consumer, container CPU/memory/restarts
- [ ] add links from metric panels to matching logs/traces using service and trace ID labels
- [ ] bind host UI to loopback and use local non-default credentials from ignored env.

## Acceptance criteria
- [ ] Grafana becomes healthy from documented observability startup
- [ ] all three data sources report healthy
- [ ] dashboard panels populate under a generated request and background event
- [ ] RED and USE panels cover each HTTP service and major dependency
- [ ] dashboards survive container recreation
- [ ] default credentials are not committed

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
