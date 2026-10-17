# PostgresDown

**Severity:** critical  
**Defined in:** [`observability/prometheus/rules/wispurl-alerts.yml`](../../observability/prometheus/rules/wispurl-alerts.yml)

## What it means

The PostgreSQL exporter in Alloy cannot connect to the database (`pg_up == 0`).

## Impact

Auth, Shortener, Analytics and Cleanup cannot read or write data. Logins, link creation and redirects fail.

## How to confirm

1. `docker compose ps postgres` and `docker compose logs --tail 100 postgres`.
2. Can the app reach it? `docker compose exec postgres pg_isready -U postgres`.
3. Is it only the exporter? Check the DSN secret has no trailing newline and uses the `wispurl_monitor` role.

## How to fix

- Postgres stopped: `docker compose up -d postgres`; services reconnect automatically.
- Disk full: free space (see HostDiskAlmostFull), then restart Postgres.
- Exporter-only failure: recreate the monitoring role (`docker compose exec postgres bash /docker-entrypoint-initdb.d/create-monitoring-role.sh`) and fix the DSN.

## After it's fixed

Confirm the alert resolves at http://127.0.0.1:9090/alerts (Alertmanager also sends a "resolved" email to Mailpit at http://127.0.0.1:8025). If the cause was new, add what you learned to this page.
