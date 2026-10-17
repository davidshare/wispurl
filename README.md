# WispURL

WispURL is a URL shortener and analytics application built from independently deployable services. Users create and manage short links, redirect through short codes, and view aggregate click analytics. The application is also a portfolio project for building a production-style DevOps, DevSecOps, and SRE platform around a real service.

The local Docker Compose application and its security and observability tooling are under active development. The AWS cloud work is currently an implementation plan; this repository does not yet provision AWS infrastructure or deploy to EKS. See the [local epic](docs/local/EPIC.md) and [cloud epic](docs/cloud/EPIC.md) for the ordered work and completion status.

## What the application does

- Creates short links using generated base62 codes or a user-selected slug, with optional expiration.
- Redirects visitors to the original URL and publishes click events asynchronously.
- Provides account authentication and an authenticated link-management and analytics dashboard.
- Aggregates click counts, daily activity, and top referrers while anonymizing IP addresses before storage.
- Generates QR code images for links.
- Applies per-user and per-action rate limits using Redis.
- Sends expiration and click-milestone notifications; local development logs notifications by default.

## Architecture

```mermaid
flowchart LR
    Browser --> Frontend[Next.js frontend]
    Frontend --> Gateway[FastAPI gateway]
    Gateway --> Auth[Auth service]
    Gateway --> Shortener[Shortener service]
    Gateway --> AnalyticsAPI[Analytics API]
    Gateway --> QR[QR service]
    Shortener --> RateLimiter[Rate limiter]
    RateLimiter --> Redis[(Redis)]
    Shortener -- link.clicked --> RabbitMQ[(RabbitMQ)]
    RabbitMQ --> AnalyticsWorker[Analytics consumer]
    AnalyticsWorker --> StatsDB[(PostgreSQL stats_db)]
    AnalyticsAPI --> StatsDB
    Auth --> AuthDB[(PostgreSQL auth_db)]
    Shortener --> ShortDB[(PostgreSQL short_db)]
    Cleanup[Cleanup worker] --> ShortDB
    Cleanup -- link.expired --> RabbitMQ
    AnalyticsWorker -- link.milestone --> RabbitMQ
    RabbitMQ --> Notifications[Notification worker]
```

The gateway is the intended public API entry point. PostgreSQL runs as one local server with separate databases for Auth, Shortener, and Analytics; services own their respective database and do not share tables or cross-service foreign keys. RabbitMQ carries click and lifecycle events so a broker or analytics outage does not need to block a redirect. JWTs are verified locally by services instead of requiring an Auth service call for every request.

### Services

| Component | Role | Data or responsibility |
| --- | --- | --- |
| [frontend](frontend/README.md) | Web application | Next.js marketing pages, authentication flows, and dashboard |
| [gateway](gateway/README.md) | Public API gateway | Routes public requests and applies shared request/security controls |
| [auth-service](auth-service/README.md) | HTTP API | Signup, login, refresh, logout, and `auth_db` ownership |
| [shortener-service](shortener-service/README.md) | HTTP API and event producer | Link lifecycle, redirects, `short_db`, and click-event publishing |
| [analytics-service](analytics-service/README.md) | Internal HTTP API | Event ingestion and aggregate statistics in `stats_db` |
| Analytics consumer | Queue worker | Consumes click events, writes analytics, and emits milestone events |
| [rate-limiter-service](rate-limiter-service/README.md) | Internal HTTP API | Atomic per-user limits backed by Redis |
| [qr-service](qr-service/README.md) | HTTP API | Stateless PNG QR generation |
| [cleanup-service](cleanup-service/README.md) | Scheduled worker | Deactivates expired links and publishes expiration events |
| [notification-service](notification-service/README.md) | Queue worker | Handles expiration and milestone notifications |

More implementation and configuration detail is available in the service READMEs.

## Technology

- **Backend:** Python 3.13, FastAPI, async SQLAlchemy, Pydantic Settings, structlog, Gunicorn/Uvicorn, and `uv`.
- **Data and messaging:** PostgreSQL, Alembic, Redis, RabbitMQ, and `aio-pika`.
- **Frontend:** Next.js, React, TypeScript, Tailwind CSS, TanStack Query, and Recharts.
- **Local secrets:** HashiCorp Vault with Raft storage, local TLS, and scripted initialization/unsealing.
- **Local observability:** Prometheus, Loki, Tempo, and Grafana Alloy. Grafana is not yet included in the local Compose stack.
- **Developer security:** Gitleaks and pre-commit.
- **Planned cloud platform:** AWS, EKS, ArgoCD, AWS Secrets Manager, Terraform, and GitHub Actions with OIDC.

## Run the project locally

This is the complete first-run walkthrough, from a fresh clone to a working app. Run every command from the repository root. The first run takes a few minutes, mostly building images.

### Prerequisites

- Docker Desktop or Docker Engine with the Compose v2 plugin, with the Docker daemon running.
- GNU Make, OpenSSL, and Python 3 (the Makefile uses `python3` to read Vault key files).
- Gitleaks and pre-commit. Step 2 installs them through Homebrew where available; on Linux, install Gitleaks first if the Makefile reports it is missing.
- Optional: `uv` and Node.js/npm, only if you plan to run a service or the frontend directly on the host.

### Step 1: Create your local configuration

```sh
cp .env.example .env
```

Generate a separate random value for each secret below by running `openssl rand -hex 32` once per value. Hex values avoid URL-escaping problems in database and broker URLs. Then edit `.env`:

| Variable | Set it to |
| --- | --- |
| `JWT_SECRET` | A random value |
| `INTERNAL_API_KEY` | A random value |
| `POSTGRES_PASSWORD` | A random value |
| `AUTH_DATABASE_URL`, `SHORTENER_DATABASE_URL`, `ANALYTICS_DATABASE_URL` | Replace the `postgres:postgres` credentials with `postgres:<POSTGRES_PASSWORD>` |
| `RABBITMQ_DEFAULT_PASS` | A random value |
| `RABBITMQ_URL` | `amqp://appuser:<RABBITMQ_DEFAULT_PASS>@rabbitmq:5672/` |

PostgreSQL applies `POSTGRES_PASSWORD` only when its data volume is first created. If you change it later, see [Troubleshooting](#troubleshooting).

`.env` is ignored by Git. Never commit it, generated Vault key material, local certificates, AppRole credentials, or the observability PostgreSQL DSN.

### Step 2: Install the secret-scanning hook

```sh
make setup
```

This installs Gitleaks and pre-commit and adds a Git hook that scans every commit for secrets.

### Step 3: Start and unseal Vault

```sh
make vault-up
docker logs -f vault-unseal
```

`make vault-up` generates local TLS certificates (first run only) and starts Vault with its unseal sidecar. The sidecar initializes Vault on first boot, then unseals it. `docker logs -f` returns when the sidecar exits; the last line should be `vault-unseal: Vault is unsealed successfully.` Confirm with:

```sh
make vault-status    # expect "Sealed  false"
```

The unseal keys and root token are written to `vault/keys/.vault-keys`. Back that file up somewhere safe; without it a sealed Vault cannot be recovered. This is a local development design, not a production KMS-backed auto-unseal setup. The Vault UI is at [https://127.0.0.1:8200/ui](https://127.0.0.1:8200/ui); the local CA is not publicly trusted.

### Step 4: Bootstrap Vault

```sh
make vault-bootstrap
```

This reads `.env`, enables the KV secrets engine and audit log, writes a scoped policy per service, and creates AppRole credentials in `vault/approles/`. Run it before Step 5: Compose mounts those AppRole files into the services, so `docker compose up` fails without them.

Rerunning it rewrites the seeded secrets and reissues AppRole credentials. Do that after changing secrets in `.env` or after a deliberate Vault reset.

### Step 5: Build and start the application

```sh
docker compose up --build -d
docker compose ps
```

Repeat `docker compose ps` until every service reports `healthy`. This starts PostgreSQL (and creates its databases), Redis, RabbitMQ, every service, and the frontend. Services apply their database migrations on startup.

### Step 6: Check that it works

```sh
curl http://localhost:8080/health    # {"status":"ok"}
```

Open [http://localhost:3000](http://localhost:3000), sign up, create a short link, open it, and check that the click appears in the dashboard analytics.

| Component | Host address | Host binding |
| --- | --- | --- |
| Frontend | `http://localhost:3000` | All interfaces in the current Compose file |
| Gateway | `http://localhost:8080` | All interfaces in the current Compose file |
| Auth API (debug) | `http://localhost:8001` | All interfaces in the current Compose file |
| Shortener API (debug) | `http://localhost:8002` | All interfaces in the current Compose file |
| pgAdmin | `http://127.0.0.1:5050` | Loopback |
| PostgreSQL | `127.0.0.1:5432` | Loopback |
| Redis | `127.0.0.1:6379` | Loopback |
| RabbitMQ management | `http://127.0.0.1:15672` | Loopback |
| Vault UI/API | `https://127.0.0.1:8200` | Loopback |

The frontend, gateway, and two debug APIs are published on all host interfaces. Treat this stack as a local development environment and do not expose it to untrusted networks. Internal services such as Analytics, QR, Cleanup, Rate Limiter, and Notification have no published host ports.

### Step 7 (optional): Start the observability stack

The observability stack runs as a separate Compose project and attaches to the application network, so Step 5 must be running first. Alloy's PostgreSQL exporter reads its connection string from an ignored secret file built from your `.env` values:

```sh
mkdir -p observability/secrets
set -a; . ./.env; set +a
printf 'postgresql://%s:%s@postgres:5432/%s?sslmode=disable\n' \
  "$POSTGRES_USER" "$POSTGRES_PASSWORD" "$POSTGRES_DB" > observability/secrets/postgres_dsn.txt
chmod 600 observability/secrets/postgres_dsn.txt

docker compose -f compose.observability.yaml up -d
```

| Component | Local address |
| --- | --- |
| Prometheus | [http://127.0.0.1:9090](http://127.0.0.1:9090) |
| Loki API | `http://127.0.0.1:3100` |
| Tempo query API | `http://127.0.0.1:3200` |
| Alloy UI | [http://127.0.0.1:12345](http://127.0.0.1:12345) |

The current observability setup has known gaps tracked in the [local issues](issues/local/README.md): Grafana is not yet deployed; Alloy's Compose healthcheck invokes `wget`, which is absent from the Alloy image, so Alloy shows as unhealthy even when it works; and the PostgreSQL exporter still needs a dedicated least-privilege monitoring account. Prometheus receives application and exporter metrics through Alloy remote write, so Alloy-scraped targets appear as `up` series rather than as entries on Prometheus's Targets page.

### Everyday commands

| Task | Command |
| --- | --- |
| Stop everything, keep data | `docker compose down` (and `docker compose -f compose.observability.yaml down`) |
| Start again later | `docker compose up -d` (the unseal sidecar runs again and unseals Vault) |
| Rebuild one service after a code change | `docker compose up --build -d <service>` |
| Follow a service's logs | `docker compose logs -f <service>` |
| Check Vault | `make vault-status` |
| List all Make targets | `make help` |

### Troubleshooting

- **`docker compose up` reports a missing `vault/approles/<service>.json`:** Vault hasn't been bootstrapped. Run Steps 3 and 4.
- **Services exit with Vault connection or authentication errors:** run `make vault-status`. If Vault is sealed, run `make vault-unseal` and then `docker compose up -d`.
- **`password authentication failed` from PostgreSQL after editing `.env`:** the password was fixed when the data volume was created. Either restore the old value, or reset local data with `docker compose down -v` (this deletes all database and broker data), then rerun `make vault-bootstrap` and Step 5.
- **A port is already in use:** another process is bound to 3000, 8080, 5432, or another port in the table above. Stop it, or change the host port in `docker-compose.yml`.

## Develop a service directly

Python services are separate `uv` projects. For example:

```sh
cd auth-service
uv sync --frozen
uv run ruff check .
uv run mypy --strict .
```

The frontend can be run locally with:

```sh
cd frontend
npm ci
npm run dev
npm run lint
npm run build
```

Each service README describes its endpoints, settings, and local run mode. The root Makefile does not currently provide a single application test-suite target; see the [local test-suite issue](docs/local/app/app-03-local-application-test-suite-and-coverage.md).

## Data, reset, and recovery

- `docker compose down` stops and removes containers but retains named volumes.
- `docker compose down -v` also removes Compose-managed data volumes, including database and broker data. Use it only when you intend to reset that local data.
- `make vault-down` stops Vault while retaining its data and local key files.
- `make vault-clean` is destructive: it deletes Vault data, key files, logs, snapshots, and generated AppRole files. A subsequent initialization creates a new Vault state; do not run it if you need the current secrets.
- `make vault-snapshot` writes a local Raft snapshot under `vault/snapshots/`; it is not an off-host backup or a completed restore test.

## Known application limitations

The Analytics README documents current follow-up work: statistics authorization confirms that a user is authenticated but does not yet prove ownership of the requested short code; click-event processing is not yet idempotent against duplicate delivery; and old click-event retention cleanup is not implemented. These and the broader reliability/security work are tracked in the local epic. Do not treat this portfolio project as production-ready until its open risks are addressed and verified.

## DevOps and SRE work plans

- [Local epic and issue index](docs/local/README.md): Docker Compose, Vault, developer security, CI, observability, Kind, Helm, ArgoCD, testing, SRE controls, and operations.
- [Cloud epic and issue index](docs/cloud/README.md): AWS foundations, VPC, EKS, managed PostgreSQL/Redis/RabbitMQ, AWS Secrets Manager, GitHub Actions OIDC, ArgoCD, observability, recovery, and cost controls.

The epics distinguish implementation subtasks from whole-issue completion. A checked subtask does not mean that all acceptance criteria for its issue are complete.

## Repository layout

```text
auth-service/             Authentication API
shortener-service/        Link management and redirects
analytics-service/        Analytics API and queue worker
gateway/                  Public API gateway
frontend/                 Next.js web application
qr-service/               QR generation API
rate-limiter-service/     Redis-backed rate limiting API
cleanup-service/          Expiration worker
notification-service/     Notification worker
shared/                   Shared Python packages copied into service builds
db/init/                  Local PostgreSQL database initialization
vault/                    Local Vault configuration and lifecycle scripts
observability/            Prometheus, Loki, Tempo, and Alloy configuration
docs/local/               Local implementation epic and grouped issues
docs/cloud/               AWS implementation epic and grouped issues
```
