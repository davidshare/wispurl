# PostgresConnectionsHigh

**Severity:** warning  
**Defined in:** [`observability/prometheus/rules/wispurl-alerts.yml`](../../observability/prometheus/rules/wispurl-alerts.yml)

## What it means

More than 80% of PostgreSQL's `max_connections` are in use.

## Impact

New connections will soon be refused, and requests that need the database will fail.

## How to confirm

1. Which clients hold connections? `docker compose exec postgres psql -U postgres -c "SELECT usename, application_name, state, count(*) FROM pg_stat_activity GROUP BY 1,2,3 ORDER BY 4 DESC;"`
2. Are many connections `idle in transaction`? That points to a code path not closing transactions.

## How to fix

- Leaking service: restart it to release connections, then fix the leak.
- Too many replicas for the pool sizes: lower `pool_size`/`max_overflow` or add PgBouncer.

## After it's fixed

Confirm the alert resolves at http://127.0.0.1:9090/alerts (Alertmanager also sends a "resolved" email to Mailpit at http://127.0.0.1:8025). If the cause was new, add what you learned to this page.
