# HighLatencyP95

**Severity:** warning  
**Defined in:** [`observability/prometheus/rules/wispurl-alerts.yml`](../../observability/prometheus/rules/wispurl-alerts.yml)

## What it means

The 95th percentile response time of a service has been above 1 second for 10 minutes.

## Impact

One request in twenty is slow. Redirects and link creation feel sluggish; timeouts may follow.

## How to confirm

1. Open the RED dashboard; compare p50, p95 and p99 for the service.
2. In Grafana Explore (Tempo), search for slow traces of the service: `{resource.service.name="<service>" && duration > 1s}`.
3. Look at which span takes the time: a SQL query, a Redis call, or a downstream HTTP call.
4. Check the USE dashboard for CPU or memory saturation.

## How to fix

- Slow query: add an index or fix the query, using the `db.statement` on the span.
- Saturated container: give it more CPU or scale out.
- Slow dependency: follow that dependency's runbook.

## After it's fixed

Confirm the alert resolves at http://127.0.0.1:9090/alerts (Alertmanager also sends a "resolved" email to Mailpit at http://127.0.0.1:8025). If the cause was new, add what you learned to this page.
