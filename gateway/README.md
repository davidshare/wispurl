# API Gateway

The single externally reachable entry point for the URL-shortener platform. It owns
no business logic — it authenticates protected routes, routes requests to the
correct internal service, and faithfully forwards the request and response.

## Responsibilities

- **Authentication.** Protected routes (`/links*`, `/stats*`) verify the access
  token locally (HS256, `exp`/`nbf`, `token_type == "access"`, `sub` → UUID) using
  the same `JWT_SECRET` as every backend service. `/auth/*` and `/qr/*` are public.
  This is *defense in depth*: each backend re-verifies the forwarded token itself —
  the gateway never injects a trusted identity header.
- **Routing.** Most-specific routes first; the bare `GET /{short_code}` catch-all is
  registered LAST and refuses reserved prefixes and non-slug input.
- **Forwarding.** One shared `httpx.AsyncClient` (`follow_redirects=False`), hop-by-hop
  headers stripped both ways, `Authorization` forwarded upstream, `X-Request-ID`
  generated/propagated, upstream connect errors → 502 and timeouts → 504.

## Routes

All API endpoints are versioned under `/v1` (the short-link redirect and `/health`
are intentionally unversioned).

| Path                         | Upstream            | Auth     |
| ---------------------------- | ------------------- | -------- |
| `GET /health`                | gateway (local)     | public   |
| `/v1/auth/{path}`            | Auth service        | public   |
| `/v1/links`, `/v1/links/{p}` | Shortener service   | required |
| `/v1/stats/{path}`           | Analytics service   | required |
| `/v1/qr/{path}`              | QR service          | public   |
| `GET /{short_code}`          | Shortener service   | public   |

## Configuration

All via environment (see root `.env.example`): `JWT_SECRET`, `JWT_ALGORITHM`,
`AUTH_SERVICE_URL`, `SHORTENER_SERVICE_URL`, `ANALYTICS_SERVICE_URL`,
`QR_SERVICE_URL`, `REQUEST_CONNECT_TIMEOUT`, `REQUEST_READ_TIMEOUT`,
`CORS_ALLOWED_ORIGINS`, `LOG_LEVEL`.

## Develop

```bash
uv sync
uv run ruff check .
uv run mypy --strict .
```
