---
id: local-023
title: Tempo trace storage and query backend
type: feat
feature: 6. Observability
status: not_started
depends_on: []
checklist_sections: 6. Observability
---

# Tempo trace storage and query backend

## Goal
Complete Tempo as the local OTLP trace backend and make stored traces queryable from Grafana.

## Implementation subtasks
- [ ] Pin Tempo image
- [ ] accept OTLP gRPC and HTTP only on the observability network
- [x] retain local WAL/blocks on a persistent volume
- [x] configure 31-day retention, ingestion limits, and max trace size
- [ ] verify retention expiry and limit behavior against a running Tempo instance
- [x] keep metrics-generator remote write to Prometheus receiver
- [ ] configure service graph/span metrics only when cardinality is bounded
- [ ] document trace UI access through Grafana
- [ ] avoid publishing receiver ports to host unless required.

## Acceptance criteria
- [x] Tempo health endpoint reports ready (HTTP 200 from `http://127.0.0.1:3200/ready` after startup)
- [ ] an OTLP test trace is accepted, persisted across container recreation, and queryable in Grafana
- [ ] trace older than configured retention is removed
- [ ] over-limit trace behavior is bounded
- [ ] Prometheus receives Tempo-generated metrics without remote-write errors

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
