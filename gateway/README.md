# API Gateway

The single externally reachable entry point. It owns no business logic — it
**authenticates** protected routes, **routes** requests to the correct internal service,
and **forwards** the request/response faithfully. FastAPI + httpx, no database.

## Routes

All API endpoints are versioned under `/v1`; the short-link redirect and `/health` are
intentionally unversioned.

| Path                          | Upstream          | Auth     |
| ----------------------------- | ----------------- | -------- |
| `GET /health`                 | gateway (local)   | public   |
| `/v1/auth/{path}`             | Auth service      | public   |
| `/v1/links`, `/v1/links/{p}`  | Shortener service | required |
| `/v1/stats/{path}`            | Analytics service | required |
| `/v1/qr/{path}`               | QR service        | public   |
| `GET /{short_code}`           | Shortener service | public   |

The catch-all `GET /{short_code}` is registered **last**, is GET-only and single-segment,
rejects reserved prefixes (`auth/links/stats/qr/health/docs/redoc/openapi.json/v1`), and
forwards to the Shortener for redirect resolution.

## How it works

- **Auth**: protected routes verify the access token **locally** (HS256 pinned, `exp`/`nbf`,
  `token_type==access`, `sub`→UUID), then forward `Authorization` upstream so the backend
  **re-verifies** (defense in depth). The gateway never injects a trusted identity header,
  and strips client-supplied `X-User-Id` / `X-Forwarded-For` / `X-Request-ID`.
- **Forwarding** (`app/proxy.py`): one shared `httpx.AsyncClient` with
  `follow_redirects=False` (so the Shortener's 307 is relayed to the browser, not followed
  here), hop-by-hop headers stripped both ways, bounded connect/read timeouts and a bounded
  connection pool. Connect errors → `502`, timeouts → `504`; upstream internals are not
  leaked beyond what backends already emit.
- **Correlation**: an `X-Request-ID` is honoured-or-generated at the edge, bound into logs,
  and propagated upstream (and the real client IP is set on `X-Forwarded-For`).
- **Hardening**: a request **body-size cap** (`413` over `MAX_BODY_BYTES`), explicit CORS
  allow-list (never `*`), and security headers (`nosniff`, HSTS, `Referrer-Policy`,
  `X-Frame-Options`). Unhandled 500s are logged with a request id.

## Configuration

| Variable | Default | Purpose |
| -------- | ------- | ------- |
| `JWT_SECRET` / `JWT_ALGORITHM` | — / `HS256` | Local token verification |
| `AUTH_SERVICE_URL` / `SHORTENER_SERVICE_URL` / `ANALYTICS_SERVICE_URL` / `QR_SERVICE_URL` | — | Upstream base URLs (fixed config, never user-controlled) |
| `REQUEST_CONNECT_TIMEOUT` / `REQUEST_READ_TIMEOUT` | `5` / `30` | Upstream timeouts (s) |
| `MAX_BODY_BYTES` | `1048576` | Max forwarded request body (1 MiB) |
| `CORS_ALLOWED_ORIGINS` | `""` | Comma-separated allow-list |
| `LOG_LEVEL` | `INFO` | structlog level |

## Run

```bash
uv sync
uv run uvicorn app.main:app --reload
uv run ruff check . && uv run mypy --strict .
```

TLS is assumed to terminate at an ingress/LB in front of the gateway; the gateway is the
only backend port published to the host.

## Layout

`app/routes` (auth, links, stats, qr, redirect) + `app/proxy.py` (forwarding engine);
`app/security/auth.py` (JWT dep), `app/config.py`, `app/errors`. `shared/` vendored
(config, JWT, logging).
