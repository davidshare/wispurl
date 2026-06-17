# Notification Service

Queue-driven (no API). Consumes `notifications.all` and emits a notification for each
`link.expired` and `link.milestone` event.

- **Default channel:** structured stdout log (`NOTIFY_CHANNEL=log`).
- **Optional SMTP/Mailtrap:** set `NOTIFY_CHANNEL=smtp` and the `SMTP_*` vars; the
  send is a clearly marked stub in `app/handlers.py` (no mail dependency by default).
- **Robustness:** manual acks after the handler succeeds; failures retried then
  dead-lettered; reconnect with backoff on broker bounce (all via
  `shared/messaging.py`). Unknown event types are logged and acked, not retried.

## Configuration

Env: `RABBITMQ_URL`, `NOTIFY_CHANNEL` (`log`|`smtp`), optional `SMTP_HOST`,
`SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM`, `LOG_LEVEL`.

## Develop

```bash
uv sync
uv run ruff check .
uv run mypy --strict .
```
