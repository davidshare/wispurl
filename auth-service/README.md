# Auth Service

Owns identity for the platform: signup, login, refresh-token rotation, and logout.
Issues short-lived HS256 access tokens that every other service verifies **locally**
(no call back to this service on the hot path). Owns its own database, `auth_db`.

Request-driven (FastAPI + async SQLAlchemy 2.0 + PostgreSQL).

## Endpoints

All API routes are versioned under `/v1`. Reached from the outside only through the
gateway (`/v1/auth/*`).

| Method | Path               | Description |
| ------ | ------------------ | ----------- |
| `POST` | `/v1/auth/signup`  | Create an account (`email` + `password`) → `201 {id, email}` |
| `POST` | `/v1/auth/login`   | → `{access_token, refresh_token}` |
| `POST` | `/v1/auth/refresh` | Rotate: returns a new pair, revokes the presented token |
| `POST` | `/v1/auth/logout`  | Revoke the refresh token → `204` |
| `GET`  | `/health`          | Readiness (checks DB connectivity); unversioned |

## How it works

- **Passwords** are hashed with **Argon2id** (cost floors validated in config). Hashing
  runs in a thread (`asyncio.to_thread`) so it never blocks the event loop.
- **Access tokens**: HS256 JWTs, 15 min, claims `sub/iat/nbf/exp/jti/token_type=access`.
  The signing secret is shared with all services via `JWT_SECRET` so they verify locally.
- **Refresh tokens**: high-entropy random strings, stored **hashed** (HMAC-SHA256) with a
  `family_id`. Every refresh **rotates** (old token revoked, new one issued). Presenting
  an already-rotated token is treated as theft and **revokes the whole family**
  (`refresh_reuse_detected` is logged).
- **No account enumeration**: login/refresh failures return a generic `401`; signup uses a
  generic message. A best-effort in-process abuse guard rate-limits auth routes (a shared
  limiter is the production upgrade).
- **Auth events** (`login_succeeded/failed`, `refresh_*`, `logout`, `signup_*`) and
  unhandled 500s are logged as structured JSON with the request id — no secrets/PII bodies.

## Tables (`auth_db`)

- `users` — `id` (UUID PK), `email` (unique), `hashed_password`, `is_active`, timestamps.
- `refresh_tokens` — `id`, `user_id` (FK), `family_id`, `token_hash` (unique), `expires_at`,
  `revoked`, `created_at`.

## Configuration

| Variable | Default | Purpose |
| -------- | ------- | ------- |
| `DATABASE_URL` | — | `postgresql+psycopg://…/auth_db` |
| `JWT_SECRET` | — | Shared HS256 secret (≥32 chars, validated) |
| `JWT_ALGORITHM` | `HS256` | Only HS256 is accepted |
| `ACCESS_TOKEN_TTL_MINUTES` | `15` | Access-token lifetime |
| `REFRESH_TOKEN_TTL_DAYS` | `7` | Refresh-token lifetime |
| `ARGON2_TIME_COST` / `ARGON2_MEMORY_COST` / `ARGON2_PARALLELISM` | `2` / `19456` / `1` | Argon2 cost (floors enforced) |
| `PASSWORD_MIN_LENGTH` / `PASSWORD_MAX_LENGTH` | `12` / `1024` | Password policy |
| `CORS_ALLOWED_ORIGINS` | `""` | Comma-separated allow-list |
| `LOG_LEVEL` | `INFO` | structlog level |

## Run

```bash
uv sync
uv run alembic upgrade head      # migrate auth_db
uv run uvicorn app.main:app --reload
uv run ruff check . && uv run mypy --strict .
```

In Docker the entrypoint runs `alembic upgrade head` then Gunicorn/Uvicorn workers; the
engine uses a bounded pool plus `statement_timeout`/`idle_in_transaction_session_timeout`.

## Layout

`app/routes` → `app/services` → `app/repositories` → `app/models`; `app/security`
(password + token helpers), `app/schemas`, `app/errors`. `shared/` is vendored (config,
JWT utils, logging) — never imported across service boundaries.
