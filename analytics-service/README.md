# Analytics Service

Owns `stats_db`. Ingests click events from the Shortener (synchronous internal HTTP
for now; RabbitMQ swap comes in Prompt 8) and serves aggregated per-short-code stats.

## Endpoints

- `POST /events` — **internal only**, gated by `X-Internal-Key`. Records one click,
  returns `202`. Never exposed through the gateway.
- `GET /stats/{short_code}` — total clicks, clicks-by-day, top referrers. Aggregates
  only; protected by access-token verification (AUTHZ option (a), see
  `app/security/auth.py`).
- `GET /health` — DB connectivity probe.

## Privacy

Client IPs are anonymized before storage (`/24` for IPv4, `/48` for IPv6); raw IPs
are never persisted. See `app/anonymize.py`. A retention purge of old rows is a
documented TODO.

## Configuration

Env: `DATABASE_URL`, `INTERNAL_API_KEY` (shared with the Shortener), `JWT_SECRET`,
`JWT_ALGORITHM`, `MILESTONES`, `TOP_REFERRERS_LIMIT`, `CORS_ALLOWED_ORIGINS`,
`LOG_LEVEL`.

## Develop

```bash
uv sync
uv run alembic upgrade head
uv run ruff check .
uv run mypy --strict .
```
