# MetricsPipelineDown

**Severity:** critical  
**Defined in:** [`observability/prometheus/rules/wispurl-alerts.yml`](../../observability/prometheus/rules/wispurl-alerts.yml)

## What it means

No `up` series for job `docker-compose-services` have reached Prometheus for 5 minutes. Alloy scrapes the apps and remote-writes to Prometheus; that path is broken.

## Impact

All application and dependency metrics have stopped. Most other alerts can no longer fire.

## How to confirm

1. Is Alloy running and healthy? `docker compose -f compose.observability.yaml ps alloy`.
2. Open the Alloy UI at http://127.0.0.1:12345 and look for unhealthy components (red).
3. Check Alloy logs for remote-write errors: `docker compose -f compose.observability.yaml logs --tail 100 alloy`.
4. Is the app stack running? Alloy only scrapes containers on the app network.

## How to fix

- Alloy crash-looping on a config error: fix `observability/alloy/config.alloy` (validate with `alloy validate`) and restart Alloy.
- Remote write failing: confirm Prometheus is healthy and started with `--web.enable-remote-write-receiver`.
- App network missing (app stack down): start it with `docker compose up -d`, then restart Alloy.

## After it's fixed

Confirm the alert resolves at http://127.0.0.1:9090/alerts (Alertmanager also sends a "resolved" email to Mailpit at http://127.0.0.1:8025). If the cause was new, add what you learned to this page.
