# Rate Limiter Service

A tiny, Redis-backed service with no database. It applies per-user, per-action
fixed-window rate limits and exists specifically to hold the one piece of shared
mutable state in the platform under concurrent access — hence the atomic
`INCR + EXPIRE` (Lua) at its core.

## Endpoints

- `POST /check` — **internal only**, gated by `X-Internal-Key`. Body
  `{user_id: UUID, action: str}`; `action` must be in the allow-list (`create_link`).
  Returns `{allowed, remaining, reset_at, limit}`. Never exposed through the gateway.
- `GET /health` — pings Redis.

## Algorithm

Fixed window: `rl:{action}:{user_id}:{window_start_epoch}` is incremented atomically;
the first increment in a window sets the TTL so keys always expire. A sliding-window
alternative (sorted set) is documented in `app/services/limiter.py` but not shipped.

## Configuration

Env: `REDIS_URL`, `INTERNAL_API_KEY` (shared with the Shortener), `WINDOW_SECONDS`,
`CREATE_LINK_LIMIT`, `LOG_LEVEL`.

## Develop

```bash
uv sync
uv run ruff check .
uv run mypy --strict .
```
