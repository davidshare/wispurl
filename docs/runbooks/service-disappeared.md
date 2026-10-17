# ServiceDisappeared

**Severity:** critical  
**Defined in:** [`observability/prometheus/rules/wispurl-alerts.yml`](../../observability/prometheus/rules/wispurl-alerts.yml)

## What it means

A service that was being scraped within the last hour has no metrics target now. Alloy only discovers running containers, so a stopped or crash-looping container disappears from monitoring instead of reporting `up = 0`. This alert catches that gap.

## Impact

The service is not running. Anything that depends on it fails: for example, if `shortener-service` is gone, redirects and link creation fail at the gateway.

## How to confirm

1. `docker compose ps -a <service>`: is the container stopped, restarting or missing?
2. `docker compose logs --tail 100 <service>`: why did it stop?
3. In Grafana, query Loki for `{service="<service>"}` around the time it disappeared.

## How to fix

- Stopped on purpose: start it again with `docker compose up -d <service>`, or ignore the alert; it resolves itself an hour after the service was last seen.
- Crash-looping: fix the error in its logs (configuration, Vault unseal, a dependency that is down), then `docker compose up -d <service>`.

## After it's fixed

Confirm the alert resolves at http://127.0.0.1:9090/alerts (Alertmanager also sends a "resolved" email to Mailpit at http://127.0.0.1:8025). If the cause was new, add what you learned to this page.
