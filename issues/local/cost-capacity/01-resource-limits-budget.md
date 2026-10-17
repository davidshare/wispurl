---
id: LOC-12.01
title: "Resource requests/limits strictly defined to prevent local resource starvation"
category: "12. Cost and Capacity Management (Local)"
status: todo
related:
  - docs/local/sre/sre-04-local-load-and-capacity-baseline-plus-retention-limits.md
---

# Resource requests/limits strictly defined to prevent local resource starvation

## What
Resource requests/limits keep the whole local stack within the machine's budget and prevent starvation.

## Current state
No limits in Compose; no cluster yet.

## Subtasks
- [ ] Set a total local budget (e.g. CPU/RAM available to Docker)
- [ ] Allocate per-service limits within it (Compose and Helm)
- [ ] Verify the full stack + observability runs under load without OOM kills

## Acceptance criteria
- [ ] Sum of limits ≤ budget, and no OOM kills during the load test

## Notes
- Implements alongside [CPU and memory limits](../container-security/06-cpu-memory-limits.md) and [Requests and limits](../kubernetes-packaging/10-resource-requests-limits.md).
