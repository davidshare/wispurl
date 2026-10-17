# DeadLetterQueueNotEmpty

**Severity:** warning  
**Defined in:** [`observability/prometheus/rules/wispurl-alerts.yml`](../../observability/prometheus/rules/wispurl-alerts.yml)

## What it means

At least one event has landed in `events.dlq` after failing processing on every retry.

## Impact

That event's work did not happen: a click was not counted, or a notification was not sent.

## How to confirm

1. Open RabbitMQ management at http://127.0.0.1:15672, queue `events.dlq`, and use **Get messages** to read one.
2. Find the failure in the consumer's logs: `{service=~"analytics-consumer-service|notification-service", level=~"error|warning"} |= "event_dropped_to_dlq"`.
3. Open the trace linked from that log line to see the failing span.

## How to fix

- Fix the bug or dependency that caused the failure first.
- Then move the messages back for reprocessing and confirm the queue drains to 0. The management UI's **Move messages** button needs the shovel plugins, which WispURL doesn't enable by default: `docker compose exec rabbitmq rabbitmq-plugins enable rabbitmq_shovel rabbitmq_shovel_management`. Without them, republish the messages to the `events` exchange with their original routing key.

## After it's fixed

Confirm the alert resolves at http://127.0.0.1:9090/alerts (Alertmanager also sends a "resolved" email to Mailpit at http://127.0.0.1:8025). If the cause was new, add what you learned to this page.
