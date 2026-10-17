# RedisDown

**Severity:** critical  
**Defined in:** [`observability/prometheus/rules/wispurl-alerts.yml`](../../observability/prometheus/rules/wispurl-alerts.yml)

## What it means

The Redis exporter cannot connect to Redis (`redis_up == 0`).

## Impact

The rate limiter cannot count requests. Link creation follows `RATE_LIMITER_FAIL_OPEN`: allowed without limits (fail-open) or rejected (fail-closed).

## How to confirm

1. `docker compose ps redis` and `docker compose logs --tail 100 redis`.
2. `docker compose exec redis redis-cli ping` should answer `PONG`.

## How to fix

- Redis stopped: `docker compose up -d redis`. Rate-limit counters restart from zero; that is expected.

## After it's fixed

Confirm the alert resolves at http://127.0.0.1:9090/alerts (Alertmanager also sends a "resolved" email to Mailpit at http://127.0.0.1:8025). If the cause was new, add what you learned to this page.
