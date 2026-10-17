---
id: LOC-6.03
title: "Application-level custom metrics exported"
category: "6. Observability (Local Stack)"
status: done
related:
  - docs/local/observability/obs-00-prometheus-metrics-collection-and-exporters.md
---

# Application-level custom metrics exported

## What
Services export their own metrics on `/metrics` for Prometheus.

## Current state
`shared/wispurl_metrics` adds middleware exporting a request counter, a latency histogram and an in-progress gauge per service; 6 HTTP services expose `/metrics` and carry scrape labels.

## Subtasks
- [x] Shared metrics library with request count, latency and in-progress metrics
- [x] `/metrics` endpoint on every HTTP service
- [x] `prometheus.io/*` labels for Alloy discovery
- [x] Low-cardinality labels (no user IDs or short codes)

## Acceptance criteria
- [x] Request rate and latency per service are queryable in Prometheus

## Notes
- Business metrics (links created, redirects, events published/consumed, DLQ writes) and worker metrics would strengthen dashboards and SLOs.

## References
- [shared/wispurl_metrics/src/wispurl_metrics/prometheus.py](../../../shared/wispurl_metrics/src/wispurl_metrics/prometheus.py)
