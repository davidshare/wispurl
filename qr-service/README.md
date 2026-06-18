# QR Code Service

Stateless — no database, no auth state. Turns a short code into a PNG QR image encoding
the full short URL. A pure input→output transformation with no shared state, so it is the
platform's horizontal-scaling showcase: run as many replicas as you like with zero
coordination. Request-driven (FastAPI + `qrcode[pil]`).

## Endpoints

| Method | Path                  | Auth | Description |
| ------ | --------------------- | ---- | ----------- |
| `GET`  | `/v1/qr/{short_code}` | public | Returns `image/png` for `PUBLIC_BASE_URL + short_code`. Optional `?size=` (square edge, px). |
| `GET`  | `/health`             | public | Liveness probe. |

## How it works

- **Validate before work**: the `short_code` is checked against the slug charset and the
  `size` is bound-checked against `MIN_SIZE_PX`/`MAX_SIZE_PX` *before* any image is
  generated — out-of-range input returns `422`. Image size is the main DoS surface, so it
  is capped up front.
- **Deterministic output** → responses carry a `Cache-Control: public, max-age=CACHE_TTL`.
- **Decoupled by design**: it does **not** verify the code exists (that would couple it to
  the Shortener/DB and break statelessness); it simply encodes the URL.
- Reached publicly through the gateway at `/v1/qr/*`.

## Configuration

| Variable | Default | Purpose |
| -------- | ------- | ------- |
| `PUBLIC_BASE_URL` | — | Base URL encoded into the QR image |
| `MIN_SIZE_PX` / `MAX_SIZE_PX` / `DEFAULT_SIZE_PX` | `64` / `1024` / `256` | Output size bounds |
| `CACHE_TTL` | `86400` | `max-age` on the PNG response |
| `LOG_LEVEL` | `INFO` | structlog level |

(`JWT_SECRET`/`JWT_ALGORITHM` are inherited from the shared settings base but unused here.)

## Run

```bash
uv sync
uv run uvicorn app.main:app --reload
uv run ruff check . && uv run mypy --strict .
```

No database, no lifespan resources — safe to scale horizontally (e.g. `deploy.replicas`).

## Layout

`app/routes/qr.py` → `app/services/qr_generator.py` (pure function); `app/schemas`,
`app/errors`. `shared/` vendored (config, logging).
