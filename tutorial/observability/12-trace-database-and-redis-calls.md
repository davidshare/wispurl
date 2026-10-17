---
title: "Observability for WispURL, Part 12: Trace Database and Redis Calls"
seo_title: "Trace SQLAlchemy and Redis Calls with OpenTelemetry"
slug: opentelemetry-sqlalchemy-redis-tracing
description: "Trace every SQL query and Redis command with OpenTelemetry's SQLAlchemy and Redis instrumentation, keep values out of spans, and silence probes."
series: "Observability for WispURL"
part: 12
date: 2026-10-17
last_updated: 2026-10-17
author: David Essien
tags: [opentelemetry, sqlalchemy, redis, postgresql, tracing, python]
keywords:
  - "OpenTelemetry SQLAlchemy async"
  - "OpenTelemetry Redis instrumentation"
  - "suppress_instrumentation health check"
  - "database spans tracing"
  - "db.statement sensitive data"
  - "trace slow SQL queries"
difficulty: intermediate
estimated_time: 30 minutes
prerequisites:
  - "Part 11: Connect Traces Across Services and Queues"
repo_files:
  - shared/wispurl_otel/src/wispurl_otel/instrumentation.py
  - auth-service/app/database.py (and shortener, analytics, cleanup)
  - rate-limiter-service/app/main.py
  - auth-service/app/main.py (and shortener, analytics)
---

# Observability for WispURL, Part 12: Trace Database and Redis Calls

> **In short:** instrument the SQLAlchemy engine (`SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)` for async engines) and the Redis client library (`RedisInstrumentor().instrument()`, before any client is created) so every query and command becomes a CLIENT span inside the request's trace. By default, SQL spans keep bound-parameter placeholders and Redis spans mask arguments, so values don't leak into traces. Wrap health checks that touch a dependency in `suppress_instrumentation()`, or each probe creates an orphan one-span trace every few seconds.

Since Part 11, a request is one trace across every service. But inside each service the spans stop at the service's edge: you can see the shortener took 38 ms, not *why*. Most of the time in a typical web request is spent waiting on a database or cache. In this part you'll add a span for every SQL statement and every Redis command.

## Design decisions

### Instrument the libraries, not the queries

As with httpx in Part 11, we instrument the **libraries** once: SQLAlchemy (which every WispURL service uses for PostgreSQL) and redis-py (used by the rate limiter). Every query and command is then traced automatically, including ones written next year.

### Keep values out of spans

A trace is often seen by more people, and kept in more places, than the database itself. A span containing `WHERE email = 'alice@example.com'` or a rate-limit key containing a user ID leaks personal data into your observability system.

The defaults are on our side here, and we keep them:

- **SQLAlchemy** records the statement with **bound-parameter placeholders**: `WHERE click_events.short_code = %(short_code_1)s`. The actual values are never added.
- **Redis** masks command arguments: `EVAL ? ? ? ?`.

Avoid enabling options that add parameter values or comments to statements unless you've checked what they expose.

### Silence probes that touch dependencies

In Part 10 we excluded `/health` from request tracing. But WispURL's health checks also *use* their dependencies: auth, shortener and analytics run `SELECT 1`, and the rate limiter sends a Redis `PING`. Once the database and Redis are traced, those calls produce spans. With no request span around them (the request itself isn't traced), each one becomes a **root span**: a separate one-span trace, from every service, every 10 seconds. They would outnumber real traces.

OpenTelemetry has a context manager for this, `suppress_instrumentation()`. Inside it, instrumentation libraries create no spans.

### The cost of more spans

Every query becomes a span. A request that runs 50 queries now produces 50 spans, which means more data to export, store and render. For WispURL's handful of queries per request, it's negligible. If you have chatty code (an N+1 query loop, say), the traces will show it clearly. That's a benefit, but it's also a reason to keep `OTEL_BSP_MAX_QUEUE_SIZE` (Part 10) as the memory ceiling, and to use sampling in production.

## Step 1: Instrumentation helpers

Two small functions in the shared library:

```python
def instrument_sqlalchemy(engine: AsyncEngine) -> None:
    """Create a span for every SQL statement sent through ``engine``."""
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)


def instrument_redis() -> None:
    """Create a span for every Redis command. Call before creating Redis clients."""
    from opentelemetry.instrumentation.redis import RedisInstrumentor

    RedisInstrumentor().instrument()
```

> `shared/wispurl_otel/src/wispurl_otel/instrumentation.py` lines 70–81.

- **`engine.sync_engine`.** WispURL uses SQLAlchemy's **async** engine. The instrumentation hooks into SQLAlchemy's engine events, which live on the synchronous engine that every async engine wraps internally. Passing the async engine itself doesn't work; pass `.sync_engine`.
- **Per-engine vs global.** The SQLAlchemy instrumentation is attached to a specific engine. Redis instrumentation patches the redis library globally, so it must run **before** a client is created, just like httpx.
- **Imports inside the functions,** for the same reason as Part 10: only services that use SQLAlchemy or Redis need those libraries installed.

The packages are `opentelemetry-instrumentation-sqlalchemy` and `opentelemetry-instrumentation-redis`, listed in the library's `pyproject.toml`.

## Step 2: Instrument each database engine

Each service that uses PostgreSQL creates its engine in `app/database.py` (`app/db.py` in cleanup). Instrument it right after creating it:

```python
from wispurl_otel import instrument_sqlalchemy

engine: AsyncEngine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
    # ...
)
# One span per SQL statement, nested under the request or message span.
instrument_sqlalchemy(engine)
```

> `auth-service/app/database.py` lines 9 and 18–31; the same in shortener, analytics and `cleanup-service/app/db.py` (line 45).

This module is imported when the app starts, which can be before `setup_otel()` has run in `main.py`. That's fine. Until a real tracer provider is registered, OpenTelemetry hands out a **proxy** tracer, which starts using the real provider as soon as `setup_otel()` registers it.

## Step 3: Instrument Redis

In the rate limiter's `app/main.py`, directly after `setup_otel`:

```python
setup_otel(service_name=os.getenv("OTEL_SERVICE_NAME", "rate-limiter-service"))
# One span per Redis command; must run before the Redis client is created.
instrument_redis()
```

> `rate-limiter-service/app/main.py` lines 38–40.

The rate limiter creates its Redis client in the FastAPI lifespan, which runs later, so the client is created after instrumentation, as required.

## Step 4: Silence the probes

The health handlers wrap their dependency check in `suppress_instrumentation()`. In the auth service:

```python
from opentelemetry.instrumentation.utils import suppress_instrumentation

    @app.get("/health", status_code=status.HTTP_200_OK, tags=["health"])
    async def health() -> JSONResponse:
        # Probes run every few seconds; don't turn each one into a database trace.
        with suppress_instrumentation():
            async with SessionLocal() as session:
                await session.execute(text("SELECT 1"))
        return JSONResponse({"status": "ok"})
```

> `auth-service/app/main.py` lines 12 and 106–112; the same in shortener and analytics.

And in the rate limiter, around Redis:

```python
        # Probes run every few seconds; don't turn each ping into a trace.
        with suppress_instrumentation():
            await redis.ping()
```

> `rate-limiter-service/app/main.py` lines 134–136.

The probe still checks the dependency for real; it just doesn't produce telemetry.

Rebuild to apply:

```sh
docker compose up --build -d
```

## Check that it works

**Database spans inside a request.** Open any redirect trace from Part 11 (`{ resource.service.name = "gateway" && name = "GET /{short_code}" }`). Under the shortener's server span you'll now find:

```text
shortener-service  CLIENT  connect
shortener-service  CLIENT  SELECT short_db
```

Click `SELECT short_db` and look at its attributes:

```text
db.system     postgresql
db.name       short_db
db.user       postgres
db.operation  SELECT short_db
db.statement  SELECT links.id, links.user_id, links.short_code, ... FROM links WHERE ...
net.peer.name postgres
```

Note `db.statement`: the query shape with placeholders, never the actual short code.

**Find slow queries across every service:**

```traceql
{ span.db.system = "postgresql" && duration > 50ms }
```

**Redis spans in link creation:**

```traceql
{ resource.service.name = "rate-limiter-service" && span.db.system = "redis" }
```

The rate limiter's spans include `EVAL` (it runs a Lua script for an atomic counter), with `db.statement = EVAL ? ? ? ?`: arguments masked.

**No probe traces.** Wait a few minutes, then check for orphaned probe spans:

```traceql
{ name = "PING" }
```

and

```traceql
{ resource.service.name = "auth-service" && name = "SELECT auth_db" && rootName = "SELECT auth_db" }
```

Both should return nothing. (`rootName` is the name of a trace's first span. A database span that's also the root means nobody was around it: an orphan.)

**The service map grows.** The service graph (Part 11) now shows `short_db`, `auth_db`, `stats_db` and `redis` as nodes, with request rates and latencies on each edge. Tempo builds these "virtual" nodes from CLIENT spans that have database attributes.

### Something the traces reveal

Look again at `db.user` on the SQL spans: **`postgres`**, the database superuser. Every WispURL service connects to PostgreSQL as the superuser, so a bug or injection flaw in any one service has full control of every database. That isn't an observability problem, but observability is how you find out. It's tracked as a security task (per-service database credentials issued by Vault) in the project's local security issues. Telemetry routinely surfaces findings like this; read your spans' attributes with a security eye now and then.

## When something goes wrong

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| No SQL spans | The async engine was passed instead of its sync engine | `SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)`. |
| No Redis spans | The client was created before instrumentation | Call `instrument_redis()` before creating any Redis client. |
| A one-span `SELECT` or `PING` trace every 10 seconds | Health checks are traced | Wrap them in `suppress_instrumentation()`. |
| SQL spans appear as separate traces in a worker | No parent span around the work | Make sure the work runs inside a CONSUMER span (Part 11) or a root span like `cleanup sweep`. |
| Parameter values visible in spans | An option that adds values or comments was enabled | Keep the defaults; check the instrumentation's options before enabling them. |

## What you have now

- A span for every SQL statement and Redis command, nested in the request's trace.
- Query shapes in spans, but never parameter values; Redis arguments masked.
- Health checks that test dependencies without flooding Tempo.
- Databases and Redis on the service map.

Logs and traces now both know which request they belong to. In [Part 13](13-link-logs-and-traces.md) we connect them, so you can jump from a log line to its trace and from a span to its logs.

## Key takeaways

- Instrument database and cache libraries once; every query and command becomes a span.
- For SQLAlchemy's async engine, instrument `engine.sync_engine`.
- Instrument globally patched libraries (Redis, httpx) before creating any client.
- Keep the privacy-friendly defaults: placeholders in SQL, masked Redis arguments.
- Use `suppress_instrumentation()` in health checks that touch dependencies, so probes don't become orphan traces.
- Read span attributes critically: they can expose real problems, like services connecting as a database superuser.

## FAQ

### How do I trace SQLAlchemy queries with OpenTelemetry?

Install `opentelemetry-instrumentation-sqlalchemy` and call `SQLAlchemyInstrumentor().instrument(engine=engine)` after creating the engine. For an async engine, pass `engine.sync_engine`. Each statement becomes a CLIENT span with `db.system`, `db.name` and `db.statement` attributes.

### Does OpenTelemetry record SQL parameter values?

Not by default in the SQLAlchemy instrumentation. `db.statement` contains the statement with bound-parameter placeholders such as `%(short_code_1)s`. Values are added only by specific opt-in options, which you should review carefully because they can put personal data into traces.

### How do I trace Redis commands in Python?

Install `opentelemetry-instrumentation-redis` and call `RedisInstrumentor().instrument()` before creating Redis clients. Each command becomes a span; arguments are masked in `db.statement` (for example `EVAL ? ? ? ?`).

### How do I stop health checks from creating traces?

Exclude the health endpoint from HTTP instrumentation (for FastAPI, `excluded_urls`), and wrap any dependency checks inside it in `opentelemetry.instrumentation.utils.suppress_instrumentation()`. Without the second step, the database or Redis calls in the health check become root spans of their own.

### Why do I see many single-span database traces?

Database calls made outside any active span, such as in health checks, background loops or start-up code, become root spans. Suppress instrumentation for probes, and wrap background work in a parent span.

---

**Series navigation:** Previous: [Part 11, Connect Traces Across Services and Queues](11-connect-traces-across-services.md) · [Series index](README.md) · Next: [Part 13, Link Logs and Traces](13-link-logs-and-traces.md)
