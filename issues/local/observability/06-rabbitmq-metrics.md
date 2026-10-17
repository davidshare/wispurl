---
id: LOC-6.06
title: "RabbitMQ metrics configured"
category: "6. Observability (Local Stack)"
status: done
related:
  - docs/local/observability/obs-00-prometheus-metrics-collection-and-exporters.md
---

# RabbitMQ metrics configured

## What
RabbitMQ metrics are collected.

## Current state
RabbitMQ enables the `rabbitmq_prometheus` plugin at start; Alloy scrapes `rabbitmq:15692`.

## Subtasks
- [x] `rabbitmq_prometheus` plugin enabled
- [x] Alloy scrape job for port 15692

## Acceptance criteria
- [x] Queue depth metrics (including `events.dlq`) are queryable

## References
- [docker-compose.yml](../../../docker-compose.yml)
- [observability/alloy/config.alloy](../../../observability/alloy/config.alloy)
