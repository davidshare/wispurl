# HighErrorRate

**Severity:** warning  
**Defined in:** [`observability/prometheus/rules/wispurl-alerts.yml`](../../observability/prometheus/rules/wispurl-alerts.yml)

## What it means

More than 5% of a service's HTTP requests returned a 5xx status over the last 5 minutes.

## Impact

Users are getting errors from that service, or from the gateway if it is the failing hop.

## How to confirm

1. Open **Service Detail** for the service (http://127.0.0.1:3001/d/wispurl-service?var-service=<service>). **5xx per second by route** shows which endpoint fails.
2. Set **Log level** to `error` and read the **Logs** panel, or in Grafana Explore run `{service="<service>", level="error"}` against Loki.
3. Open a trace from the **Failed requests** panel, or from a log line's **View trace** link, to see which hop failed.
4. Check dependency alerts (Postgres, Redis, RabbitMQ) that may explain it.

## How to fix

- Dependency down: follow that dependency's runbook.
- Bad deploy: roll back to the previous image and redeploy.
- Upstream timeouts at the gateway (504s): find the slow service in the trace.

## After it's fixed

Confirm the alert resolves at http://127.0.0.1:9090/alerts (Alertmanager also sends a "resolved" email to Mailpit at http://127.0.0.1:8025). If the cause was new, add what you learned to this page.
