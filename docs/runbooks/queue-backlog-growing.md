# QueueBacklogGrowing

**Severity:** warning  
**Defined in:** [`observability/prometheus/rules/wispurl-alerts.yml`](../../observability/prometheus/rules/wispurl-alerts.yml)

## What it means

A queue has more than 1000 messages waiting for 10 minutes: consumers are not keeping up.

## Impact

Analytics and notifications are delayed. If it keeps growing, RabbitMQ memory and disk usage climb.

## How to confirm

1. Open **Workers & Messaging** (http://127.0.0.1:3001/d/wispurl-workers). **Messages waiting by queue** shows which queue is growing and **Consumers by queue** shows whether anything is reading it (0 means the consumer is gone).
2. Is the consumer running? `docker compose ps analytics-consumer-service notification-service`.
3. Is it failing and retrying? The **Outcome per second** panel shows `retry` results; the worker's logs show `event_retry`. **Processing time p95** shows whether each message got slower.

## How to fix

- Consumer stopped: start it.
- Consumer slow: scale it (`docker compose up -d --scale analytics-consumer-service=2`) or fix the slow dependency.

## After it's fixed

Confirm the alert resolves at http://127.0.0.1:9090/alerts (Alertmanager also sends a "resolved" email to Mailpit at http://127.0.0.1:8025). If the cause was new, add what you learned to this page.
