# TargetDown

**Severity:** critical  
**Defined in:** [`observability/prometheus/rules/wispurl-alerts.yml`](../../observability/prometheus/rules/wispurl-alerts.yml)

## What it means

Prometheus (or Alloy, for app services and exporters) has failed every scrape of a target for 2 minutes.

## Impact

Metrics for that target are missing, so dashboards and other alerts for it are blind. If the target is an app service, it is probably not serving traffic either.

## How to confirm

1. Open http://127.0.0.1:9090/alerts and note the `job` and `instance` labels.
2. Is the container running? `docker compose ps` (app) or `docker compose -f compose.observability.yaml ps` (observability).
3. Read its logs: `docker compose logs --tail 100 <service>`.
4. From inside the network, can the metrics endpoint be reached? `docker compose exec gateway python -c "import urllib.request;print(urllib.request.urlopen('http://<service>:8000/metrics',timeout=2).status)"`

## How to fix

- Container stopped or crash-looping: fix the error in its logs, then `docker compose up -d <service>`.
- Container healthy but not scraped: check its `prometheus.io/*` labels and that it is on the app network.
- Only observability jobs down: check that container with `docker compose -f compose.observability.yaml logs <service>`.

## After it's fixed

Confirm the alert resolves at http://127.0.0.1:9090/alerts (Alertmanager also sends a "resolved" email to Mailpit at http://127.0.0.1:8025). If the cause was new, add what you learned to this page.
