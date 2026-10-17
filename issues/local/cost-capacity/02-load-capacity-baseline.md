---
id: LOC-12.02
title: "Local load and capacity tests executed to establish baseline performance"
category: "12. Cost and Capacity Management (Local)"
status: todo
related:
  - docs/local/sre/sre-04-local-load-and-capacity-baseline-plus-retention-limits.md
---

# Local load and capacity tests executed to establish baseline performance

## What
Load tests establish baseline throughput, latency and the saturation point.

## Current state
None.

## Subtasks
- [ ] Run the k6 scenarios at stepped load
- [ ] Record RPS, p95/p99, error rate, and CPU/memory per service
- [ ] Identify the first bottleneck
- [ ] Write `docs/sre/capacity-baseline.md`

## Acceptance criteria
- [ ] Baseline document with numbers and the identified bottleneck
