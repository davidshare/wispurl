# QueueBacklogGrowing

**Severity:** warning  
**Defined in:** [`observability/prometheus/rules/wispurl-alerts.yml`](../../observability/prometheus/rules/wispurl-alerts.yml)

## What it means

A queue has more than 1000 messages waiting for 10 minutes: consumers are not keeping up.

## Impact

Analytics and notifications are delayed. If it keeps growing, RabbitMQ memory and disk usage climb.

## How to confirm

1. Check the **RabbitMQ messages per queue** panel on the USE dashboard.
2. Is the consumer running? `docker compose ps analytics-consumer-service notification-service`.
3. Is it failing and retrying? Check its logs for `event_retry`.

## How to fix

- Consumer stopped: start it.
- Consumer slow: scale it (`docker compose up -d --scale analytics-consumer-service=2`) or fix the slow dependency.

## After it's fixed

Confirm the alert resolves at http://127.0.0.1:9090/alerts (Alertmanager also sends a "resolved" email to Mailpit at http://127.0.0.1:8025). If the cause was new, add what you learned to this page.
