# QR Code Service

Stateless, no database, no auth state. Turns a short code into a PNG QR image
encoding the full short URL. Being a pure input->output transformation with no shared
state, it is the platform's horizontal-scaling showcase — run as many replicas as
you like with zero coordination.

## Endpoints

- `GET /qr/{short_code}` — returns `image/png`. Optional `?size=` (square edge in px,
  bound-checked against `MIN_SIZE_PX`/`MAX_SIZE_PX`; out-of-range → 422). The code is
  validated against the slug charset before any work. Does **not** verify the code
  exists (that would couple it to the Shortener); it just encodes
  `PUBLIC_BASE_URL + short_code`.
- `GET /health` — liveness probe.

## Configuration

Env: `PUBLIC_BASE_URL`, `MIN_SIZE_PX`, `MAX_SIZE_PX`, `DEFAULT_SIZE_PX`, `CACHE_TTL`,
`LOG_LEVEL`.

## Develop

```bash
uv sync
uv run ruff check .
uv run mypy --strict .
```
