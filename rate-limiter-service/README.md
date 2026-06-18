# Rate Limiter Service

A tiny, Redis-backed service with **no database**. It applies per-user, per-action
fixed-window rate limits and exists specifically to hold the one piece of shared mutable
state in the platform under concurrent access — hence the atomic `INCR + EXPIRE` (Lua) at
its core. Request-driven (FastAPI + `redis.asyncio`).

## Endpoint

| Method | Path        | Auth | Description |
| ------ | ----------- | ---- | ----------- |
| `POST` | `/v1/check` | `X-Internal-Key` | `{user_id: UUID, action: str}` → `{allowed, remaining, reset_at, limit}`. **Internal only** — never routed through the gateway. |
| `GET`  | `/health`   | public | Pings Redis. |

`action` must be in the allow-list (`create_link`) and `user_id` must be a UUID — together
these bound the Redis key space.

## Algorithm

Fixed window keyed `rl:{action}:{user_id}:{window_start_epoch}`. A single Lua script does
`INCR` then, on the first increment of a window, `EXPIRE` — so a counter is **never** left
without a TTL (no leaked keys). A request is allowed while the post-increment count is
within the configured limit. A sliding-window alternative (sorted set) is documented in
`app/services/limiter.py` but not shipped.

## Failure behaviour

The Redis client has bounded `socket_timeout`/`socket_connect_timeout`, so a hung Redis
can't block a worker. If Redis is unreachable the service returns a deliberate **503**
(`LimiterUnavailableError`) rather than an opaque 500 — and the Shortener **fails open** on
a non-200, so a limiter outage degrades to "allow", it doesn't block link creation.

## Configuration

| Variable | Default | Purpose |
| -------- | ------- | ------- |
| `REDIS_URL` | — | Backing store |
| `INTERNAL_API_KEY` | — | Validates `/v1/check` callers (constant-time) |
| `WINDOW_SECONDS` | `3600` | Fixed-window length |
| `CREATE_LINK_LIMIT` | `20` | Allowed `create_link` per window |
| `LOG_LEVEL` | `INFO` | structlog level |

(`JWT_SECRET`/`JWT_ALGORITHM` are inherited from the shared settings base but unused here.)

## Run

```bash
uv sync
uv run uvicorn app.main:app --reload
uv run ruff check . && uv run mypy --strict .
```

A single async Redis client (with its internal connection pool) is opened in the app
lifespan. No migrations — counters are ephemeral and TTL-expired by design.

## Layout

`app/routes/check.py` → `app/services/limiter.py`; `app/security/internal.py`
(internal-key dep), `app/schemas`, `app/errors`. `shared/` vendored (config, logging).
