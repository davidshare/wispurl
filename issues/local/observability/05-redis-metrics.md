---
id: LOC-6.05
title: "Redis metrics configured"
category: "6. Observability (Local Stack)"
status: done
related:
  - docs/local/observability/obs-00-prometheus-metrics-collection-and-exporters.md
---

# Redis metrics configured

## What
Redis metrics are collected.

## Current state
Alloy runs `prometheus.exporter.redis` against `redis:6379`.

## Subtasks
- [x] Redis exporter in Alloy
- [x] Scraped every 15s and remote-written

## Acceptance criteria
- [x] `redis_up` = 1

## References
- [observability/alloy/config.alloy](../../../observability/alloy/config.alloy)
