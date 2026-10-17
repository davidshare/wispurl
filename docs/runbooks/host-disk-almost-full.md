# HostDiskAlmostFull

**Severity:** warning  
**Defined in:** [`observability/prometheus/rules/wispurl-alerts.yml`](../../observability/prometheus/rules/wispurl-alerts.yml)

## What it means

Less than 10% of the Docker host's root filesystem is free. On Docker Desktop this is Docker's VM disk.

## Impact

When the disk fills, Postgres, RabbitMQ, Loki, Tempo and Prometheus stop writing and may crash.

## How to confirm

1. `docker system df` shows what is using space.
2. Check observability volumes: retention is 15d/5GB (Prometheus), 31d (Loki and Tempo).

## How to fix

- Remove unused images and build cache: `docker image prune` and `docker builder prune`.
- Lower retention in `compose.observability.yaml`, `observability/loki/loki.yaml` or `observability/tempo/tempo.yaml`.
- On Docker Desktop, increase the VM disk size in Settings → Resources.

## After it's fixed

Confirm the alert resolves at http://127.0.0.1:9090/alerts (Alertmanager also sends a "resolved" email to Mailpit at http://127.0.0.1:8025). If the cause was new, add what you learned to this page.
