---
id: LOC-6.11
title: "Trace storage and visualization with Tempo or Jaeger"
category: "6. Observability (Local Stack)"
status: done
related:
  - docs/local/observability/obs-02-tempo-trace-storage-and-query-backend.md
---

# Trace storage and visualization with Tempo or Jaeger

## What
Tempo stores traces and Grafana visualises them.

## Current state
Tempo runs with OTLP/Jaeger receivers, local storage, 744h block retention and a metrics generator that remote-writes to Prometheus. There's no visualisation until Grafana exists.

## Subtasks
- [x] Tempo service with persistent volume
- [x] OTLP receivers (fed by Alloy)
- [x] Block retention configured
- [x] Add Tempo as a Grafana data source (with traces→logs and service graph)
- [x] Enable metrics-generator processors (`service-graphs`, `span-metrics`) in overrides
- [x] Add a healthcheck and pin the image
- [x] Stop publishing unused receiver ports (14250/14268) to the host if not needed

## Acceptance criteria
- [x] A trace can be found and viewed in Grafana Explore

## References
- [observability/tempo/tempo.yaml](../../../observability/tempo/tempo.yaml)
