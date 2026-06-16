# Microservices URL Shortener

Foundation scaffold for a microservices URL shortener. This repository currently contains only shared conventions and local backing stores: Postgres, Redis, and RabbitMQ.

No service logic exists yet.

## Bring Up Stores

Copy `.env.example` to `.env` when running locally, then start the backing stores:

```bash
docker compose up postgres redis rabbitmq
```

Postgres runs a first-boot init script that creates:

- `auth_db`
- `short_db`
- `stats_db`

RabbitMQ management UI is exposed at `http://localhost:15672`.

## Build Order

1. Finalize shared settings, logging, and token conventions.
2. Add the auth service and its database migrations.
3. Add the shortener service and its database migrations.
4. Add analytics event publishing and consumer storage.
5. Add rate limiting and QR services.
6. Add gateway/routing, CI checks, and deployment manifests.
