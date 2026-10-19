---
title: "Observability for WispURL: The Complete Series"
seo_title: "Self-Hosted Observability for Microservices: Full Guide"
slug: microservices-observability-series
description: "A 17-part, hands-on series building metrics, logs, traces, dashboards and alerts for a Python microservices app with Prometheus, Grafana, Loki, Tempo and Alloy."
series: "Observability for WispURL"
date: 2026-10-17
last_updated: 2026-10-17
author: David Essien
tags: [observability, prometheus, grafana, loki, tempo, opentelemetry, alloy, docker-compose]
keywords:
  - "microservices observability tutorial"
  - "Prometheus Grafana Loki Tempo tutorial"
  - "Grafana Alloy tutorial"
  - "OpenTelemetry Python tutorial"
  - "Docker Compose monitoring stack"
---

# Observability for WispURL: The Complete Series

> **In short:** a hands-on series that builds a complete, self-hosted observability stack for a Python microservices application, one tool at a time. It covers metrics (Prometheus), logs (Loki), traces (Tempo and OpenTelemetry), one collector for all three (Grafana Alloy), dashboards (Grafana) and alerting (Alertmanager), all with Docker Compose. Every part explains the design decisions behind it and ends with a way to check that it works.

The demo application is **WispURL**, a URL shortener made of ten services, PostgreSQL, Redis and RabbitMQ. The series focuses on the DevOps and SRE work; application code only appears where a tool needs the application's help.

## The parts

| Part | Article | What you'll learn |
| --- | --- | --- |
| 0 | [What We're Building](00-the-observability-plan.md) | The three signals, the tools, why each was chosen, and how data flows |
| 1 | [Start the Stack with Prometheus](01-start-the-stack-with-prometheus.md) | Run Prometheus with Docker Compose, size retention, validate config |
| 2 | [Expose RED Metrics from the Services](02-expose-red-metrics-from-the-services.md) | Request metrics in FastAPI, label cardinality, Gunicorn multiprocess mode |
| 3 | [Collect Service Metrics with Grafana Alloy](03-collect-service-metrics-with-alloy.md) | Discover containers, scrape them and remote-write to Prometheus |
| 4 | [Monitor PostgreSQL, Redis and RabbitMQ](04-monitor-postgres-redis-rabbitmq.md) | Embedded exporters, a least-privilege database user, per-queue metrics |
| 5 | [Host and Container Metrics](05-host-and-container-metrics.md) | Node and cAdvisor metrics from Alloy, and the USE method |
| 6 | [Deploy Grafana](06-deploy-grafana.md) | Grafana with secrets and data sources provisioned as code |
| 7 | [Store Logs in Loki](07-store-logs-in-loki.md) | Loki with schema, limits and enforced retention |
| 8 | [Ship Container Logs with Alloy](08-ship-container-logs-with-alloy.md) | Parse, label, redact and join logs before they reach Loki |
| 9 | [Store Traces in Tempo](09-store-traces-in-tempo.md) | Tempo 3, OTLP through Alloy, and metrics generated from traces |
| 10 | [Instrument Services with OpenTelemetry](10-instrument-services-with-opentelemetry.md) | A shared tracing library, sampling and export settings |
| 11 | [Connect Traces Across Services and Queues](11-connect-traces-across-services.md) | Context propagation over HTTP and RabbitMQ |
| 12 | [Trace Database and Redis Calls](12-trace-database-and-redis-calls.md) | SQL and Redis spans, and keeping probe noise out of traces |
| 13 | [Link Logs and Traces](13-link-logs-and-traces.md) | Trace IDs in logs and one-click jumps between Loki and Tempo |
| 14 | [Production Dashboards as Code](14-dashboards-as-code.md) | Overview, per-service drill-down, business and infrastructure dashboards generated from Python |
| 15 | [Alerting with Prometheus and Alertmanager](15-alerting-with-alertmanager.md) | Alert rules, routing, inhibition and local email with Mailpit |
| 16 | [Runbooks for Every Alert](16-runbooks-for-alerts.md) | Turning alerts into actions people can follow |

## Versions used

Prometheus `v3.15.0`, Grafana Alloy `v1.20.1`, Loki `3.7.8`, Tempo `3.1.0`, Grafana `13.2.4`, Alertmanager `v0.34.1`, Mailpit `v1.31.6`, OpenTelemetry Python `1.45.1` (instrumentation `0.66b1`).
