---
id: LOC-6.02
title: "Grafana deployed locally with pre-configured dashboards"
category: "6. Observability (Local Stack)"
status: done
related:
  - docs/local/observability/obs-04-grafana-dashboards-and-data-sources.md
---

# Grafana deployed locally with pre-configured dashboards

## What
Grafana runs locally with data sources and dashboards provisioned from code.

## Current state
Grafana is not deployed (README lists it as a known gap).

## Subtasks
- [x] Add a pinned `grafana` service on loopback (e.g. `:3001`, since `:3000` is the frontend)
- [x] Admin credentials from a secret file, not defaults
- [x] Provision data sources: Prometheus, Loki and Tempo (logs→traces and traces→logs links, service map; exemplars skipped: needs Prometheus exemplar storage)
- [x] Provision dashboards from `observability/grafana/dashboards/*.json`
- [x] Persist Grafana state in a volume

## Acceptance criteria
- [x] Fresh `docker compose -f compose.observability.yaml up` shows working data sources and dashboards
