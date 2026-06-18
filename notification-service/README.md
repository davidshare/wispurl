# Notification Service

Queue-driven — **no API, no database**. Consumes `notifications.all` and emits a
notification for each `link.expired` and `link.milestone` event. This is the platform's
third execution pattern (alongside request- and schedule-driven). aio-pika consumer.

## How it works

- Consumes the `notifications.all` queue (bound to routing keys `link.expired` and
  `link.milestone`) and dispatches each event to a per-type handler (`app/handlers.py`).
- **Robustness** (via `shared/messaging.py`): durable queues + persistent messages; manual
  ack only **after** the handler succeeds; failures retried with capped backoff then
  **dead-lettered**; payloads validated as a Pydantic `EventEnvelope` (malformed → DLQ);
  reconnect with exponential backoff on a broker bounce. Unknown event types are logged and
  acked (not retried — they aren't poison).
- **Channels**: default is a structured stdout log (`NOTIFY_CHANNEL=log`). An optional
  SMTP/Mailtrap path (`NOTIFY_CHANNEL=smtp` + `SMTP_*`) is a clearly marked stub in
  `app/handlers.py` — no mail dependency is pulled in by default.

## Configuration

| Variable | Default | Purpose |
| -------- | ------- | ------- |
| `RABBITMQ_URL` | — | Broker connection |
| `NOTIFY_CHANNEL` | `log` | `log` or `smtp` |
| `SMTP_HOST` / `SMTP_PORT` / `SMTP_USERNAME` / `SMTP_PASSWORD` / `SMTP_FROM` | — / `587` / … | Used only when `NOTIFY_CHANNEL=smtp` |
| `LOG_LEVEL` | `INFO` | structlog level |

## Run

```bash
uv sync
uv run python -m app.main
uv run ruff check . && uv run mypy --strict .
```

## Layout

`app/main.py` (consumer entrypoint) → `app/consumer.py` (dispatch) → `app/handlers.py`
(per-event handlers + delivery channel); `app/config.py`. `shared/` vendored
(logging, messaging).
