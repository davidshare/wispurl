# Analytics Service

Records link clicks and serves aggregated per-short-code statistics. Owns its own
database, `stats_db`. Runs in **two execution modes** from the same image:

- **API** (request-driven) — `app.main:app` for `/v1/events` and `/v1/stats`.
- **Consumer** (queue-driven) — `python -m app.worker` consumes click events from RabbitMQ.

FastAPI + async SQLAlchemy 2.0 + PostgreSQL + aio-pika.

## Endpoints

| Method | Path                    | Auth | Description |
| ------ | ----------------------- | ---- | ----------- |
| `POST` | `/v1/events`            | `X-Internal-Key` | Record one click → `202`. **Internal only** — never routed through the gateway. |
| `GET`  | `/v1/stats/{short_code}`| access token | Total clicks, clicks-by-day, top referrers (aggregates only). |
| `GET`  | `/health`               | public | Readiness (DB check). |

## Consumer (`python -m app.worker`)

Consumes `analytics.clicks` (routing key `link.clicked`) and writes each click via the
**same** service method the HTTP `/v1/events` handler uses (no duplicated write logic).
Acks are manual and happen only after a successful insert; failures are retried with
backoff, then dead-lettered. Runs at `prefetch=1` so milestone crossings are detected
exactly once — when a click pushes a code's total across a threshold it publishes a
`link.milestone` event.

## Data & privacy

- Table `click_events`: `id`, `short_code` (indexed), `clicked_at` (indexed),
  `ip_address`, `referrer`, `user_agent`. Composite `(short_code, clicked_at)` index
  supports the time-bucketed aggregation, which is done **in SQL** (`GROUP BY`).
- **IPs are anonymized before storage** (`/24` for IPv4, `/48` for IPv6) — raw IPs are
  never persisted (`app/anonymize.py`). `/v1/stats` returns aggregates only, never rows.
- **Known gaps** (documented in code): `/v1/stats` proves the caller is logged in, not
  that they *own* the code; click ingestion is not yet deduplicated against at-least-once
  redelivery; a retention purge of old `click_events` is a TODO.

## Configuration

| Variable | Default | Purpose |
| -------- | ------- | ------- |
| `DATABASE_URL` | — | `…/stats_db` |
| `INTERNAL_API_KEY` | — | Validates `/v1/events` callers (constant-time) |
| `JWT_SECRET` / `JWT_ALGORITHM` | — / `HS256` | `/v1/stats` access-token verification |
| `RABBITMQ_URL` | — | Consumer + milestone publishing |
| `MILESTONES` | `100,1000,10000` | Click thresholds that fire `link.milestone` |
| `TOP_REFERRERS_LIMIT` | `5` | Top-N referrers returned |
| `CORS_ALLOWED_ORIGINS` / `LOG_LEVEL` | `""` / `INFO` | — |

## Run

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload     # API
uv run python -m app.worker              # consumer
uv run ruff check . && uv run mypy --strict .
```

The DB engine uses a bounded pool + `statement_timeout`/`idle_in_transaction_session_timeout`;
budget connections across the API workers *and* the consumer process.

## Layout

`app/routes` (events, stats) → `app/services` → `app/repositories` → `app/models`;
`app/worker.py` (consumer), `app/anonymize.py`, `app/security` (internal-key + JWT),
`app/schemas`, `app/errors`. `shared/` vendored (config, JWT, logging, messaging).
