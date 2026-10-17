---
id: LOC-6.01
title: "Prometheus deployed locally for metrics scraping"
category: "6. Observability (Local Stack)"
status: done
related:
  - docs/local/observability/obs-00-prometheus-metrics-collection-and-exporters.md
---

# Prometheus deployed locally for metrics scraping

## What
Prometheus is the local metrics store for application and dependency metrics.

## Current state
In `compose.observability.yaml`: loopback port, remote-write receiver (Alloy pushes everything), self + Alloy scrape jobs, 15d retention and a healthcheck.

## Subtasks
- [x] Prometheus service with persistent volume
- [x] Remote-write receiver enabled for Alloy and Tempo
- [x] Scrape Prometheus and Alloy
- [x] Time-based retention configured
- [x] UI bound to loopback

## Acceptance criteria
- [x] `up` returns 1 for the app services and exporters (via Alloy remote write)

## Notes
- Image still `:latest` — see [Pin image versions](../container-security/07-pin-image-versions.md).

## References
- [compose.observability.yaml](../../../compose.observability.yaml)
- [observability/prometheus/prometheus.yml](../../../observability/prometheus/prometheus.yml)
