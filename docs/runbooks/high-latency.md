# HighLatencyP95

**Severity:** warning  
**Defined in:** [`observability/prometheus/rules/wispurl-alerts.yml`](../../observability/prometheus/rules/wispurl-alerts.yml)

## What it means

The 95th percentile response time of a service has been above 1 second for 10 minutes.

## Impact

One request in twenty is slow. Redirects and link creation feel sluggish; timeouts may follow.

## How to confirm

1. Open **Service Detail** for the service (http://127.0.0.1:3001/d/wispurl-service?var-service=<service>); compare p50, p95 and p99, and use **p95 latency by route** to find the slow endpoint. The **Slowest recent requests** panel lists traces you can open directly.
2. In Grafana Explore (Tempo), search for slow traces of the service: `{resource.service.name="<service>" && duration > 1s}`.
3. Look at which span takes the time: a SQL query, a Redis call, or a downstream HTTP call.
4. Check the **Resources** row on the same page, or the **Containers** dashboard, for CPU or memory saturation. The **Dependencies (from traces)** row shows whether an outgoing SQL, Redis or HTTP call got slower.

## How to fix

- Slow query: add an index or fix the query, using the `db.statement` on the span.
- Saturated container: give it more CPU or scale out.
- Slow dependency: follow that dependency's runbook.

## After it's fixed

Confirm the alert resolves at http://127.0.0.1:9090/alerts (Alertmanager also sends a "resolved" email to Mailpit at http://127.0.0.1:8025). If the cause was new, add what you learned to this page.
