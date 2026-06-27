# WispURL

A production-shaped **URL shortener built as a microservices system**. WispURL takes a long URL and returns a short link, serves the public redirect, and records and aggregates click analytics — but the real point of the project is the architecture around that simple core: independent services that own their own data, three different execution patterns (request-, queue-, and schedule-driven), an async event backbone, and a single hardened gateway in front of a polished Next.js web client.

Everything runs locally with one `docker compose up`.

## What it does

- **Shorten** — create short links (random base62 or a custom slug, optional expiry), list and delete your own links.
- **Redirect** — fast public `307` redirect from a short code to the original URL.
- **Analyze** — every click is published as an event, anonymized, and aggregated into per-link stats (total clicks, clicks-by-day, top referrers).
- **QR** — generate a PNG QR code for any short link.
- **Notify** — emit notifications when a link expires or crosses a click milestone.
- **Expire & clean up** — a scheduled sweep deactivates expired links.
- **Rate limit** — per-user, per-action limits backed by Redis.
- **A full web app** — marketing site, auth, and an authenticated dashboard with charts.

## Architecture



```
                     ┌────────────┐

Browser ───────────►  │  Frontend  │  Next.js web client (BFF for auth)
└─────┬──────┘
│  /v1/* (only public entry point)
┌─────▼──────┐
│  Gateway   │  authenticate · route · forward
└─────┬──────┘
┌───────────────┬──────┼───────────────┬──────────────┐
▼               ▼      ▼               ▼              ▼
┌──────────┐  ┌────────────┐  ┌───────────┐  ┌───────────┐  ┌──────────┐
│   Auth   │  │ Shortener  │  │ Analytics │  │    QR     │  │   Rate   │
│ (auth_db)│  │ (short_db) │  │ (stats_db)│  │(stateless)│  │ Limiter  │
└──────────┘  └─────┬──────┘  └─────▲─────┘  └───────────┘  └────┬─────┘
│ link.clicked   │ consume                Redis
▼                │
┌───────────────── RabbitMQ ──────────────────┐
│ link.clicked · link.expired · link.milestone │
└───────┬───────────────────────────┬─────────┘
▼                            ▼
┌──────────────┐            ┌────────────────┐
│   Cleanup    │            │  Notification  │
│ (schedule)   │            │   (consumer)   │
└──────────────┘            └────────────────┘

```

**Three execution patterns, by design:**

- **Request-driven** — Auth, Shortener, Analytics (API), QR, Rate Limiter, Gateway (FastAPI).
- **Queue-driven** — Analytics consumer and Notification service (aio-pika consumers).
- **Schedule-driven** — Cleanup sweep (a loop locally; a Kubernetes CronJob in production).

**Principles:** each service owns its own database (no shared tables, no cross-service foreign keys); the gateway is the only thing exposed publicly; access tokens are verified **locally** by every service (no hot-path call back to Auth); services are decoupled through RabbitMQ events rather than synchronous calls wherever possible.

---

## Services

| Service | Type | Store | Responsibility |
| ------- | ---- | ----- | -------------- |
| [gateway](./gateway) | API | — | Single public entry point: authenticate, route, forward. |
| [auth-service](./auth-service) | API | `auth_db` | Signup/login/refresh/logout; issues HS256 JWTs; rotating refresh tokens. |
| [shortener-service](./shortener-service) | API + producer | `short_db` | Create/list/delete links; public redirect; publishes `link.clicked`. |
| [analytics-service](./analytics-service) | API + consumer | `stats_db` | Ingests click events, serves aggregated stats; anonymizes IPs. |
| [qr-service](./qr-service) | API | — | Stateless PNG QR generator (horizontal-scaling showcase). |
| [rate-limiter-service](./rate-limiter-service) | API | Redis | Atomic per-user, per-action fixed-window limits (Lua `INCR`+`EXPIRE`). |
| [cleanup-service](./cleanup-service) | Schedule | `short_db` | Sweeps expired links, publishes `link.expired`. |
| [notification-service](./notification-service) | Consumer | — | Notifies on `link.expired` and `link.milestone`. |
| [frontend](./frontend) | Web | — | Next.js client: marketing site, auth, dashboard. |

Each service has its own README with endpoints, internals, and configuration.

---

## Tech Stack

- **Backend** — Python 3.13, FastAPI, async SQLAlchemy 2.0, Pydantic Settings, structlog, Gunicorn/Uvicorn, `uv` for dependency management. Auth via PyJWT + Argon2id.
- **Messaging** — RabbitMQ (aio-pika): durable queues, persistent messages, manual acks, capped-backoff retries, and dead-letter queues.
- **Data** — PostgreSQL (one database per stateful service, Alembic migrations), Redis.
- **Frontend** — Next.js (App Router, RSC, Turbopack), React, TypeScript (strict), Tailwind CSS v4, shadcn/ui, TanStack Query v5, Zustand, react-hook-form + zod, Recharts.
- **Quality** — `ruff` + `mypy --strict` across every Python service.

---

## Event Flow

1. A redirect (`GET /{short_code}`) emits a fire-and-forget `link.clicked` event — a broker outage never breaks the redirect.
2. The **Analytics consumer** writes each click (IP anonymized to `/24` ÷ `/48`) and, when a code crosses a configured threshold (`MILESTONES`), publishes `link.milestone`.
3. The **Cleanup** sweep deactivates expired links and publishes `link.expired`.
4. The **Notification** service consumes `link.milestone` and `link.expired` and dispatches a notification (stdout log by default; optional SMTP stub).

---

## Security Highlights

- **Local JWT verification** everywhere (HS256 pinned, `exp`/`nbf`/`token_type` checked) — the shared `JWT_SECRET` lets services verify without calling Auth.
- **Rotating refresh tokens** stored hashed, with reuse/theft detection that revokes a whole token family.
- **BOLA-safe** authorization: ownership is filtered at the query level, never trusted from the request body.
- **Gateway hardening**: body-size cap, explicit CORS allow-list, security headers, strips client-supplied identity/forwarding headers, request-id correlation.
- **Frontend session model**: access token in memory only; refresh token in an httpOnly, SameSite=Strict cookie set by same-origin BFF routes; single-flight refresh so the rotating token is never double-spent.
- **Internal-only endpoints** (Analytics `/v1/events`, Rate Limiter `/v1/check`) are guarded by a constant-time `X-Internal-Key` and never routed through the gateway.

---

## Project Setup & Local Security Initialization

This project utilizes a centralized **Gitleaks security policy** along with a native `Makefile` automation layer to protect both the Python microservices backend and the Next.js frontend. This ensures that cryptographic secrets, JWT signatures, and internal API keys are automatically intercepted and blocked *before* they leave your local machine.

### Prerequisites

Ensure you have the following installed on your host machine:
* **Docker & Docker Compose**
* **GNU Make** (Standard on macOS/Linux; available via `chocolatey` or `winget` on Windows)

### 1. Security & Hooks Initialization

Before writing code or executing commits, run the primary repository bootstrap command at the project root. This command checks for the **Gitleaks binary**, installs it dynamically if missing (using your native package manager), and configures a local, isolated pre-commit hook strategy.

```bash
make setup

```

* **To execute a manual deep scan** of the entire historical repository tree:
```bash
make scan

```


* **To safely uninstall** local security hooks and wipe configurations:
```bash
make clean

```



### 2. Environment Configuration

WispURL relies on environment-driven variables to securely distribute secrets (like the shared JWT token validator) across isolated Docker container environments.

Duplicate the template file at the root level and inject cryptographically strong random hashes:

```bash
cp .env.example .env

```

Open the newly created `.env` file and replace the default keys with secure placeholders:

```env
JWT_SECRET=your_long_random_hmac_sha256_signing_key_here
INTERNAL_API_KEY=your_secure_constant_time_internal_service_key_here

```

### 3. Orchestration & Local Bootstrapping

With local git hooks initialized and environment boundaries defined, fire up the complete multi-database event-driven stack via Docker Compose.

The initial boot automatically invokes the database initializers inside `db/init/` to build separate instances for `auth_db`, `short_db`, and `stats_db`:

```bash
docker compose up --build

```

Once the logging stream stabilizes, verify accessibility across the critical system edge coordinates:

| Portal | Interface URL | Credentials / Layer |
| --- | --- | --- |
| **Web UI Application** | `http://localhost:3000` | Frontend Next.js Client Dashboard |
| **Hardened API Gateway** | `http://localhost:8080` | Core Public `/v1/*` Entry Routing |
| **Event Broker Console** | `http://localhost:15672` | RabbitMQ Management (`appuser` / `apppass`) |

### Published Ports

| Port | Service |
| --- | --- |
| `3000` | Frontend |
| `8080` | Gateway (public API) |
| `8001` / `8002` | Auth / Shortener (direct, for debugging) |
| `5432` / `6379` | Postgres / Redis |
| `5672` / `15672` | RabbitMQ / management UI |

Analytics, QR, Rate Limiter, Cleanup, and Notification publish no host ports — they are reached only on the internal Docker network or through the gateway.

---

## Working on a Single Service

Each Python service is a standalone `uv` project:

```bash
cd auth-service
uv sync
uv run uvicorn app.main:app --reload     # API services
uv run ruff check . && uv run mypy --strict .

```

The frontend:

```bash
cd frontend
npm install
npm run dev                              # http://localhost:3000

```

Every service vendors a small `shared/` module (config base, JWT utils, structured logging) so they share conventions without a runtime coupling.

---

## Roadmap

The codebase is structured for a DevOps phase: container images per service, Kubernetes manifests (Cleanup becomes a CronJob, QR scales horizontally), CI running `ruff`/`mypy`/the frontend build, and the production upgrades flagged in the service READMEs (shared rate limiter for auth routes, click-event deduplication, analytics retention purge, ownership checks on stats).
