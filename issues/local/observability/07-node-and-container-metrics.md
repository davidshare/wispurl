---
id: LOC-6.07
title: "Node and container metrics via Node Exporter and cAdvisor"
category: "6. Observability (Local Stack)"
status: done
related:
  - docs/local/observability/obs-00-prometheus-metrics-collection-and-exporters.md
---

# Node and container metrics via Node Exporter and cAdvisor

## What
Host and per-container resource metrics (USE) are collected.

## Current state
None.

## Subtasks
- [x] Add `prometheus.exporter.unix` (or a node-exporter container) in Alloy
- [x] Add `prometheus.exporter.cadvisor` (or a cAdvisor container) with the required mounts
- [x] Document Docker Desktop/macOS limitations (metrics reflect the Linux VM)
- [x] Label series with the Compose service name

## Acceptance criteria
- [x] `container_memory_working_set_bytes` is queryable per Compose service
