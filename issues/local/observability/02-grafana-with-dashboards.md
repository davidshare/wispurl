---
id: LOC-6.02
title: "Grafana deployed locally with pre-configured dashboards"
category: "6. Observability (Local Stack)"
status: todo
related:
  - docs/local/observability/obs-04-grafana-dashboards-and-data-sources.md
---

# Grafana deployed locally with pre-configured dashboards

## What
Grafana runs locally with data sources and dashboards provisioned from code.

## Current state
Grafana is not deployed (README lists it as a known gap).

## Subtasks
- [ ] Add a pinned `grafana` service on loopback (e.g. `:3001`, since `:3000` is the frontend)
- [ ] Admin credentials from a secret file, not defaults
- [ ] Provision data sources: Prometheus, Loki and Tempo (traces↔logs links, exemplars)
- [ ] Provision dashboards from `observability/grafana/dashboards/*.json`
- [ ] Persist Grafana state in a volume

## Acceptance criteria
- [ ] Fresh `docker compose -f compose.observability.yaml up` shows working data sources and dashboards
