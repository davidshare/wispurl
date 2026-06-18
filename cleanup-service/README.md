# Cleanup Service

Schedule-driven — **not an API**. Periodically sweeps `short_db` for links whose
`expires_at` has passed and are still active, deactivates them in batches, and publishes a
`link.expired` event per deactivated link. Async SQLAlchemy Core + aio-pika.

## How it works

- **The sweep** (`app/service.py`): selects active, past-expiry rows in batches of
  `BATCH_SIZE`, sets `is_active = false` via a single `UPDATE … WHERE id IN (…)`, and
  returns the affected short codes. A partial index in `short_db`
  (`ix_links_active_expiry (expires_at) WHERE is_active`) keeps the sweep off a seq scan.
- **Idempotent**: only active, past-expiry rows are selected, so a re-run is a no-op.
- **Publish** (`app/publisher.py`): one `link.expired` event per deactivated code. A
  publish failure is logged and swallowed (at-most-once expiry notification) — the link
  stays correctly deactivated, so the next sweep won't reprocess it.
- **Resilience** (`app/main.py`): a wedged sweep can't hold locks forever
  (`statement_timeout`/`idle_in_transaction_session_timeout`, small bounded pool), and the
  loop reconnects with capped backoff on a DB/broker outage rather than crashing.
- **Direct DB access**: connects to `short_db` directly (a batch maintenance job, not
  request-path logic). The tradeoff vs a Shortener internal "expire" endpoint is documented
  in `app/db.py`. It owns no migrations — it depends on the Shortener's schema.

> In the DevOps phase this becomes a Kubernetes **CronJob** (one sweep per invocation, no
> long-running loop). The Compose container loops with a sleep only for local dev.

## Configuration

| Variable | Default | Purpose |
| -------- | ------- | ------- |
| `DATABASE_URL` | — | `…/short_db` (the Shortener's DB) |
| `RABBITMQ_URL` | — | Publishes `link.expired` |
| `CLEANUP_INTERVAL_SECONDS` | `60` | Sleep between sweeps |
| `BATCH_SIZE` | `500` | Rows deactivated per batch |
| `LOG_LEVEL` | `INFO` | structlog level |

## Run

```bash
uv sync
uv run python -m app.main
uv run ruff check . && uv run mypy --strict .
```

## Layout

`app/main.py` (loop) → `app/service.py` (sweep) + `app/publisher.py`; `app/db.py`
(engine + Core `links` table mapping); `app/config.py`. `shared/` vendored
(logging, messaging).
