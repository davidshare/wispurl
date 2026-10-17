---
id: cloud-030
title: Cloud load test and scaling baseline
type: feat
feature: 3. Testing
status: not_started
depends_on: [cloud-018, cloud-023]
checklist_sections: 3. Testing; 13. Cost and Capacity
---

# Cloud load test and scaling baseline

## Goal
Re-run representative WispURL load scenarios against AWS and compare with the local baseline without uncontrolled spend.

## Implementation subtasks
- [ ] Use bounded k6 scenarios for auth, short-link create/redirect, analytics ingest/query and QR
- [ ] record VUs, duration, request/data cap, service version, AZ and instance sizes
- [ ] measure p50/p95/p99, error rate, throughput, CPU/memory, DB connections, Redis and RabbitMQ saturation
- [ ] exercise HPA/node scaling
- [ ] set abort thresholds and cleanup generated records.

## Acceptance criteria
- [ ] Run produces a versioned report and dashboard links
- [ ] load stays within approved request and spend limits
- [ ] autoscaling and connection limits behave within documented bounds
- [ ] differences from local baseline are explained
- [ ] run is repeatable with the same parameters

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
