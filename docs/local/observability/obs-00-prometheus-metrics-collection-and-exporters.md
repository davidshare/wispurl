---
id: local-020
title: Prometheus metrics collection and exporters
type: feat
feature: 6. Observability
status: not_started
depends_on: []
checklist_sections: 6. Observability
---

# Prometheus metrics collection and exporters

## Goal
Complete the existing Prometheus service as the authoritative local metrics store for application and dependency health.

## Implementation subtasks
- [ ] Pin a supported Prometheus image and configure bounded local retention/storage
- [x] preserve remote-write receiver for Alloy/Tempo metrics generation
- [x] scrape Prometheus and Alloy
- [x] configure discovery and relabeling for Compose services opted in through scrape labels
- [x] verify expected application targets are UP after starting the full local stack; Prometheus query `up` returned value `1` for all six Compose-labeled HTTP services through Alloy remote write, plus Redis, RabbitMQ, and PostgreSQL exporters. These appear as remote-written series, not as direct Prometheus `/api/v1/targets` entries.
- [ ] add Node Exporter and cAdvisor for host/container USE metrics
- [ ] add PostgreSQL exporter with a dedicated read-only monitoring user and Docker secret
- [x] retain Redis exporter and RabbitMQ Prometheus plugin targets
- [x] add scrape jobs for every application endpoint
- [x] use stable service/environment labels and avoid high-cardinality user/link IDs
- [x] expose UI on loopback only.

## Acceptance criteria
- [x] Prometheus targets for all expected jobs are UP in a fresh local stack (verified with the `up` query: all six labeled HTTP services and the configured Redis, RabbitMQ, and PostgreSQL exporters returned `1`)
- [ ] application request metrics and DB/Redis/RabbitMQ/node/container metrics are queryable
- [ ] a deliberately stopped exporter turns its target DOWN and recovers
- [ ] retention uses configured bounded storage
- [ ] no password is present in Prometheus config or labels

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
