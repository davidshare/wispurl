# Shortener Service

The core service: creates short links, lists/deletes the caller's links, and serves the
public redirect. Owns its own database, `short_db`. Request-driven (FastAPI + async
SQLAlchemy 2.0 + PostgreSQL) and a RabbitMQ **producer** for click events.

## Endpoints

| Method   | Path             | Auth         | Description |
| -------- | ---------------- | ------------ | ----------- |
| `POST`   | `/v1/links`      | access token | Create a link (`long_url`, optional `custom_slug`, `expires_at`) → `201` |
| `GET`    | `/v1/links`      | access token | List the caller's links (paginated) |
| `DELETE` | `/v1/links/{id}` | access token | Delete one of the caller's links → `204` |
| `GET`    | `/{short_code}`  | public       | **307** redirect to the long URL (unversioned) |
| `GET`    | `/health`        | public       | Readiness (DB check) |

## How it works

- **Auth**: access tokens are verified **locally** (HS256 pinned, `exp`/`nbf`,
  `token_type==access`, `sub`→UUID). The owner is always the JWT `sub` — never the body.
- **Authorization (BOLA-safe)**: list/delete filter at the query level
  (`WHERE id AND user_id`); another user's id returns `404`, never their data.
- **Input**: `long_url` must be `http(s)` (no `javascript:`/`data:`), max 2048 chars;
  `custom_slug` is charset + reserved-word checked; `expires_at` must be future;
  pagination is bounded.
- **Short codes**: random base62 with a uniqueness retry (custom-slug collision → `409`,
  exhausted generation → `503`). `short_code` is DB-unique (race-safe).
- **Redirect path**: emits a `link.clicked` event to RabbitMQ as a fire-and-forget
  background task — a broker outage never breaks the 307 (the click may be dropped, the
  documented tradeoff). A legacy direct HTTP post to Analytics is available behind a flag.
- **Rate limiting**: calls the Rate Limiter (`/v1/check`) before creating a link, and by
  default **fails open** (configurable) so a limiter outage doesn't block creation.
- **Open redirect / SSRF**: redirecting to a user URL is intentional and kept safe by the
  `http(s)`-only rule; the server never fetches `long_url` itself.

## Table (`short_db.links`)

`id` (UUID PK), `user_id` (indexed; no cross-service FK), `short_code` (unique),
`long_url`, `created_at`, `expires_at`, `is_active`. Partial index
`ix_links_active_expiry (expires_at) WHERE is_active` supports the Cleanup sweep.

## Configuration

| Variable | Default | Purpose |
| -------- | ------- | ------- |
| `DATABASE_URL` | — | `…/short_db` |
| `JWT_SECRET` / `JWT_ALGORITHM` | — / `HS256` | Local token verification |
| `PUBLIC_BASE_URL` | — | Base for the returned `short_url` |
| `RATE_LIMITER_URL` / `ANALYTICS_SERVICE_URL` | — | Internal dependencies |
| `INTERNAL_API_KEY` | — | Sent to internal limiter/analytics endpoints |
| `RABBITMQ_URL` | — | Click-event publishing |
| `EVENTS_PUBLISH_ENABLED` | `true` | Publish `link.clicked` to the queue |
| `ANALYTICS_HTTP_FALLBACK` | `false` | Also POST clicks over HTTP (legacy) |
| `RATE_LIMITER_FAIL_OPEN` | `true` | Allow creates when the limiter is unreachable |
| `RATE_LIMITER_REQUEST_TIMEOUT` / `ANALYTICS_REQUEST_TIMEOUT` | `1` / `2` | Downstream timeouts (s) |
| `SHORTCODE_LENGTH` / `SHORTCODE_MAX_RETRIES` | `7` / `5` | Code generation |
| `DEFAULT_PAGE_LIMIT` / `MAX_PAGE_LIMIT` | `50` / `100` | Pagination |
| `CORS_ALLOWED_ORIGINS` / `LOG_LEVEL` | `""` / `INFO` | — |

## Run

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
uv run ruff check . && uv run mypy --strict .
```

The DB engine uses a bounded pool + `statement_timeout`/`idle_in_transaction_session_timeout`.
A shared `httpx.AsyncClient` and the RabbitMQ publisher are opened in the app lifespan.

## Layout

`app/routes` (links, redirect) → `app/services` (link, shortcode, rate_limit, analytics) →
`app/repositories` → `app/models`; `app/security/auth.py` (JWT dep), `app/schemas`,
`app/errors`. `shared/` vendored (config, JWT, logging, messaging).
