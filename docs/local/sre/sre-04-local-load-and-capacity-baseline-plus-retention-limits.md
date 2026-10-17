---
id: local-039
title: Local load and capacity baseline plus retention limits
type: feat
feature: 12. Cost and Capacity Management
status: not_started
depends_on: [local-020, local-021, local-031]
checklist_sections: 12. Cost and Capacity Management; 3. Testing
---

# Local load and capacity baseline plus retention limits

## Goal
Measure local service capacity and ensure logs, metrics, traces, DB and broker volumes cannot exhaust a developer machine.

## Implementation subtasks
- [ ] Create k6 scenario for registration/login, short-link create/redirect, analytics event ingest/query and QR
- [ ] record machine/Compose versions, duration, concurrency, latency percentiles and errors
- [ ] establish resource budgets for Compose and Kubernetes
- [ ] bound Prometheus, Loki, Tempo, Alloy, PostgreSQL, Redis and RabbitMQ retention/storage
- [ ] alert or document behavior near volume cap.

## Acceptance criteria
- [ ] Baseline report is reproducible and records p50/p95/p99 plus throughput and error rate
- [ ] resource limits are configured for every service
- [ ] telemetry retention matches documented days and volume caps
- [ ] a test volume threshold produces visible alert or deterministic cleanup
- [ ] baseline is labeled local-only

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
