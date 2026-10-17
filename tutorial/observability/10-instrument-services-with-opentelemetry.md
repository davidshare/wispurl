---
title: "Observability for WispURL, Part 10: Instrument Services with OpenTelemetry"
seo_title: "OpenTelemetry in Python FastAPI: A Shared Tracing Setup"
slug: opentelemetry-python-fastapi-tracing-setup
description: "Add OpenTelemetry tracing to FastAPI services with one shared library: OTLP export to Alloy, sampling, batching limits and probe exclusion."
series: "Observability for WispURL"
part: 10
date: 2026-10-17
last_updated: 2026-10-17
author: David Essien
tags: [opentelemetry, python, fastapi, tracing, otlp, gunicorn]
keywords:
  - "OpenTelemetry Python FastAPI"
  - "OpenTelemetry sampling parentbased"
  - "OTEL_BSP_MAX_QUEUE_SIZE"
  - "FastAPIInstrumentor excluded_urls"
  - "OpenTelemetry Gunicorn"
  - "OTLP exporter Python"
  - "manual vs auto instrumentation"
difficulty: intermediate
estimated_time: 40 minutes
prerequisites:
  - "Part 9: Store Traces in Tempo"
repo_files:
  - shared/wispurl_otel/src/wispurl_otel/instrumentation.py
  - shared/wispurl_otel/pyproject.toml
  - docker-compose.yml
  - gateway/app/main.py (and the other HTTP services)
---

# Observability for WispURL, Part 10: Instrument Services with OpenTelemetry

> **In short:** put OpenTelemetry setup in one shared Python package. `setup_otel()` creates a `TracerProvider` with the service's name, a `BatchSpanProcessor` and an OTLP gRPC exporter pointed at Alloy; `instrument_fastapi()` creates a server span per request but skips `/health` and `/metrics`. Configure everything that varies between environments with standard `OTEL_*` variables in Compose: sampling (`parentbased_always_on` locally), batch sizes, queue limits and the exporter timeout, which the Python exporter reads in **seconds**. Export runs in the background, so a missing collector never slows or breaks a request.

Tempo is ready to store traces (Part 9). Now the services have to create them. In this part you'll give every HTTP service a **server span** for each request it handles. Part 11 connects those spans across services and through RabbitMQ; Part 12 adds database and Redis spans.

## How tracing works inside a service

OpenTelemetry in Python has a few moving parts:

| Part | Job |
| --- | --- |
| **TracerProvider** | The central object. Creates tracers, holds the sampler, owns the span processors. One per process. |
| **Resource** | Attributes describing *what* produced the spans: `service.name`, environment, version. Attached to every span. |
| **Sampler** | Decides whether a new trace is recorded at all. |
| **Span processor** | What happens to finished spans. `BatchSpanProcessor` queues them and exports in batches on a background thread. |
| **Exporter** | Sends batches somewhere. Ours sends OTLP over gRPC to Alloy. |
| **Instrumentation** | Library-specific hooks that create spans for you, such as one per FastAPI request or one per httpx call. |

## Design decisions

### OpenTelemetry, not a vendor SDK

Tracing code lives inside every service and is expensive to change later. Vendor SDKs (Datadog, New Relic) tie that code to one product. OpenTelemetry is the open standard all major backends accept, so the services will never need to change when the backend does. The move to AWS later only changes where Alloy forwards spans.

### Explicit setup, not zero-code instrumentation

OpenTelemetry offers **zero-code** (auto) instrumentation: install `opentelemetry-distro` and start your app with `opentelemetry-instrument gunicorn ...`, and it patches every supported library at start-up, configured entirely through environment variables. It's a great way to try tracing quickly.

We use a small explicit library instead, because:

- **Control.** We decide exactly what's traced, for example excluding probe endpoints, and silencing health checks that touch the database (Part 12).
- **Workers.** WispURL's queue workers aren't web servers. Explicit setup works the same for a FastAPI app and a plain `asyncio` worker.
- **Readability.** A new team member can read one 80-line file and know exactly what tracing does. With auto-instrumentation, the behaviour is spread across environment variables and library patches.
- **One place to change.** Like the metrics library in Part 2, every service gets identical tracing from one package.

The trade-off is that new libraries aren't traced automatically; you add one line to the shared library when you need them.

### Configure with standard environment variables

The library contains almost no settings. Everything that differs between environments (where spans go, how many are kept, timeouts) comes from the standard `OTEL_*` environment variables, which every OpenTelemetry SDK understands. Locally they're set in `docker-compose.yml`; in Kubernetes they'd be set in a manifest. The code never changes.

### Sampling: record everything locally, a fraction in production

A **sampler** decides at the start of a trace whether to record it. Options include:

| Sampler | Records | Use |
| --- | --- | --- |
| `always_on` | Every trace | Development, low traffic |
| `traceidratio` + `OTEL_TRACES_SAMPLER_ARG=0.1` | About 10% of traces, chosen from the trace ID | High traffic, to control cost |
| `parentbased_*` | Follows the caller's decision when there is a caller; uses the named sampler otherwise | **Almost always what you want** |

The `parentbased_` part matters in microservices. Without it, each service decides independently: the gateway might record a trace while the shortener drops its half, leaving a trace with holes. With it, the **first** service decides, and that decision travels with the request (Part 11), so every service records or drops the trace together.

We use `parentbased_always_on` locally: every trace, and an easy switch to `parentbased_traceidratio` in production.

This is **head sampling**: the decision is made at the start, before anyone knows whether the request will fail. **Tail sampling** decides after the trace is complete (for example "keep all errors and slow requests, plus 5% of the rest") but needs a collector that buffers whole traces. Alloy can do this with `otelcol.processor.tail_sampling` when you need it.

### Export must never hurt requests

Tracing is diagnostic. It must never slow down or break the thing it diagnoses. `BatchSpanProcessor` ensures that:

- finished spans go into an in-memory **queue**, and the request carries on immediately;
- a background thread exports batches from the queue;
- if the collector is slow or down, export retries and then gives up; when the queue is full, new spans are **dropped**, not waited on.

So the worst a tracing failure can do is lose some spans. With the collector stopped for ten minutes during testing for this series, every service kept serving normally, logging `Transient error StatusCode.UNAVAILABLE ... retrying`, and traces resumed when the collector came back.

### Don't trace probes

Docker health checks hit `/health` every 10 seconds per service, and Alloy scrapes `/metrics` every 15 seconds. Traced, they'd outnumber real requests and bury them. They say nothing about user traffic, so they're excluded.

## Step 1: The shared tracing library

`shared/wispurl_otel/src/wispurl_otel/instrumentation.py` holds the setup. The start-up function:

```python
EXCLUDED_URLS = "/health$,/ready$,/live$,/metrics$"

_configured = False


def setup_otel(service_name: str) -> None:
    global _configured
    if _configured:
        return
    _configured = True
    if os.getenv("OTEL_SDK_DISABLED", "false").lower() == "true":
        return

    # Resource.create also merges OTEL_RESOURCE_ATTRIBUTES (environment, version).
    resource = Resource.create({"service.name": service_name})
    # The sampler comes from OTEL_TRACES_SAMPLER / OTEL_TRACES_SAMPLER_ARG.
    provider = TracerProvider(resource=resource)
    # The exporter reads OTEL_EXPORTER_OTLP_ENDPOINT and _TIMEOUT; the batch
    # processor reads OTEL_BSP_*. Export runs on a background thread, so a slow or
    # missing collector never blocks a request: spans are retried, then dropped.
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(provider)

    # (httpx instrumentation: explained in Part 11)
    if importlib.util.find_spec("httpx") is not None:
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

        HTTPXClientInstrumentor().instrument()
```

> `instrumentation.py` lines 23–60.

Line by line:

- **`_configured`** makes the function safe to call twice. Setting a second global tracer provider is an error in OpenTelemetry.
- **`OTEL_SDK_DISABLED=true`** turns tracing off entirely, which is useful for running tests without a collector.
- **`Resource.create({"service.name": ...})`** names the service. `Resource.create` also merges `OTEL_RESOURCE_ATTRIBUTES` from the environment, which is how `deployment.environment=local` and `service.version` get onto every span.
- **`TracerProvider(resource=resource)`** with no explicit sampler reads `OTEL_TRACES_SAMPLER` from the environment.
- **`BatchSpanProcessor(OTLPSpanExporter())`**: both read their settings from the environment, as described in Step 2.
- **`trace.set_tracer_provider(provider)`** registers it globally, so every instrumentation library finds it.

Request tracing for FastAPI:

```python
def instrument_fastapi(app: FastAPI) -> None:
    """Create a server span for every incoming request, except probes."""
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    FastAPIInstrumentor.instrument_app(app, excluded_urls=EXCLUDED_URLS)
```

> `instrumentation.py` lines 63–67.

`excluded_urls` is a comma-separated list of regular expressions, each matched against the full URL. Anchoring them with `$` (`/health$`) excludes `/health` without accidentally excluding a route like `/health-report`.

The FastAPI and httpx imports sit **inside** the functions, not at the top of the file. The queue workers install this library but not FastAPI or httpx. A top-level `import` would crash them at start-up with `ModuleNotFoundError: No module named 'fastapi'`. Importing where it's used means each service only needs the libraries it actually uses.

### The package's dependencies

```toml
dependencies = [
    "opentelemetry-api>=1.45.1",
    "opentelemetry-exporter-otlp-proto-grpc>=1.45.1",
    "opentelemetry-instrumentation-fastapi>=0.66b1",
    "opentelemetry-instrumentation-httpx>=0.66b1",
    "opentelemetry-instrumentation-redis>=0.66b1",
    "opentelemetry-instrumentation-sqlalchemy>=0.66b1",
    "opentelemetry-sdk>=1.45.1",
]
```

> `shared/wispurl_otel/pyproject.toml`.

OpenTelemetry versions come in pairs: the API and SDK (`1.45.1`) and the instrumentation packages (`0.66b1`) are released together and must match. Each service's `uv.lock` pins the exact versions; the `>=` minimum here stops any service from resolving an older, mismatched set. When upgrading, upgrade all of them together and re-lock every service.

## Step 2: Configure it in Compose

All the settings live in one anchor at the top of `docker-compose.yml`:

```yaml
x-otel-env: &otel-env
  OTEL_EXPORTER_OTLP_PROTOCOL: grpc
  OTEL_EXPORTER_OTLP_ENDPOINT: http://alloy:4317

  OTEL_TRACES_EXPORTER: otlp
  OTEL_METRICS_EXPORTER: none
  OTEL_LOGS_EXPORTER: none

  OTEL_PROPAGATORS: tracecontext,baggage
  OTEL_RESOURCE_ATTRIBUTES: deployment.environment=local,service.version=1.0.0

  # Sampling: keep every trace locally. parentbased_ means a service follows the
  # caller's decision, so a trace is never half-recorded. In production use
  # parentbased_traceidratio with OTEL_TRACES_SAMPLER_ARG=0.1 (10%).
  OTEL_TRACES_SAMPLER: parentbased_always_on
  # Export limits: spans wait at most 5 s before being sent in batches of up to
  # 512; at most 2048 wait in memory (extra spans are dropped, never blocking a
  # request). The Python exporter reads the timeout in seconds.
  OTEL_BSP_SCHEDULE_DELAY: "5000"
  OTEL_BSP_MAX_EXPORT_BATCH_SIZE: "512"
  OTEL_BSP_MAX_QUEUE_SIZE: "2048"
  OTEL_EXPORTER_OTLP_TIMEOUT: "10"
```

> `docker-compose.yml` lines 16–37.

Each service merges the anchor and adds its own name:

```yaml
    environment:
      <<: *otel-env
      OTEL_SERVICE_NAME: "auth-service"
```

The settings our code actually uses:

| Variable | Value | Meaning |
| --- | --- | --- |
| `OTEL_SERVICE_NAME` | `auth-service` | The service's name in Tempo and Grafana. It matches the Compose service and the metrics and logs `service` label (Part 2). |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://alloy:4317` | Where to send spans. The `http://` scheme means plain text, which is fine on the private Docker network. |
| `OTEL_EXPORTER_OTLP_TIMEOUT` | `10` | How long one export may take. **Careful:** the OpenTelemetry spec defines this in milliseconds, but the Python OTLP exporter reads it as **seconds**. `10` means 10 seconds here, and `10000` would mean nearly three hours. |
| `OTEL_RESOURCE_ATTRIBUTES` | `deployment.environment=local,...` | Extra attributes on every span, for telling environments and versions apart. |
| `OTEL_TRACES_SAMPLER` | `parentbased_always_on` | See *Sampling*. |
| `OTEL_PROPAGATORS` | `tracecontext,baggage` | How trace context is written into requests: the W3C standard headers. Part 11. |
| `OTEL_BSP_SCHEDULE_DELAY` | `5000` (ms) | Export at least every 5 seconds. |
| `OTEL_BSP_MAX_EXPORT_BATCH_SIZE` | `512` | Up to 512 spans per export. |
| `OTEL_BSP_MAX_QUEUE_SIZE` | `2048` | At most 2,048 spans waiting in memory per process. Past that, new spans are dropped. This is the memory ceiling for tracing. |

`OTEL_EXPORTER_OTLP_PROTOCOL`, `OTEL_TRACES_EXPORTER`, `OTEL_METRICS_EXPORTER` and `OTEL_LOGS_EXPORTER` are read by zero-code instrumentation, not by our explicit setup (which always uses the gRPC exporter for traces only). They're kept because they describe the intent accurately, and they'll be correct if someone runs a service with `opentelemetry-instrument`.

These values are the SDK defaults, written out on purpose. Defaults you can't see are defaults nobody reviews; written down, they're visible in code review and easy to tune.

## Step 3: Wire it into each service

In each HTTP service's `app/main.py`, call `setup_otel` at module level, **before** the app and any httpx clients are created, and `instrument_fastapi` right after creating the app:

```python
import os

from wispurl_otel import setup_otel, instrument_fastapi

setup_otel(service_name=os.getenv("OTEL_SERVICE_NAME", "gateway"))

def create_app() -> FastAPI:
    app = FastAPI(...)
    instrument_fastapi(app)
    # middleware, routes ...
```

> `gateway/app/main.py` lines 10, 23, 43, 104 and 112.

Two things to know about Gunicorn:

- **Gunicorn forks worker processes.** OpenTelemetry's background export thread doesn't survive a `fork()`. WispURL's entrypoints start Gunicorn *without* `--preload`, so each worker imports the app (and runs `setup_otel`) itself, after forking, and gets its own working exporter. If you ever add `--preload`, move `setup_otel` into Gunicorn's `post_fork` hook, or exports will silently stop.
- **The service name has a fallback** (`"gateway"`) so the service still works if someone forgets `OTEL_SERVICE_NAME`, but Compose always sets it.

Each service also needs the library in its `pyproject.toml` (`"wispurl-otel"` plus a `[tool.uv.sources]` path entry, exactly like `wispurl-metrics` in Part 2), and a rebuild:

```sh
docker compose up --build -d
```

## Check that it works

Use the app for a minute: sign in, create a link, open it a few times. Then in Grafana → **Explore** → **Tempo** → **TraceQL**:

```traceql
{ resource.service.name = "gateway" }
```

You'll see a list of traces, one per request, named after the route template, such as `GET /{short_code}` or `POST /v1/links`. Open one: the root is the gateway's **server** span, with attributes such as `http.method`, `http.route`, `http.status_code` and `http.target`.

These are OpenTelemetry's older HTTP attribute names, which the Python instrumentation still uses by default. The newer stable names are `http.request.method`, `http.response.status_code` and `url.path`. Setting `OTEL_SEMCONV_STABILITY_OPT_IN=http` switches to them, and `http/dup` emits both during a migration. Pick one and use it consistently in queries and dashboards.

**Probes aren't traced.** This should return nothing:

```traceql
{ name =~ "GET /(health|metrics)" }
```

**Find failing or slow requests.** TraceQL filters on span properties:

```traceql
{ resource.service.name = "gateway" && status = error }
{ resource.service.name = "gateway" && duration > 200ms }
```

**Check the resource attributes.** Open any span's **Resource** section: `service.name`, `deployment.environment=local` and `service.version=1.0.0` are all there.

**Prove tracing can't take a service down.** Stop the collector, use the app, then look at a service's logs:

```sh
docker compose -f compose.observability.yaml stop alloy
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8080/health
docker compose logs --tail 5 gateway
docker compose -f compose.observability.yaml start alloy
```

The request still returns `200`. The logs show `Transient error StatusCode.UNAVAILABLE encountered while exporting traces to alloy:4317, retrying`. Once Alloy is back, new traces appear again.

At this point, each trace contains only **one** service. The gateway's trace stops at the gateway, and the shortener starts a separate trace for the same request. Connecting them is Part 11.

## When something goes wrong

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| No traces at all | `setup_otel` not called, or the endpoint is wrong | Check `OTEL_EXPORTER_OTLP_ENDPOINT=http://alloy:4317` and that Alloy is on the app network. |
| `ModuleNotFoundError: No module named 'fastapi'` in a worker | The library imports FastAPI at module level | Import instrumentations inside the functions that use them. |
| Traces stop after a while under Gunicorn | `--preload` with tracing set up before fork | Remove `--preload`, or call `setup_otel` in a `post_fork` hook. |
| Health checks flood Tempo | Probes not excluded | Pass `excluded_urls` to `FastAPIInstrumentor`. |
| `Overriding of current TracerProvider is not allowed` | Setup called twice | Guard it, as `_configured` does. |
| Exports hang for hours | Timeout given in milliseconds | The Python OTLP exporter reads `OTEL_EXPORTER_OTLP_TIMEOUT` in seconds. |

## What you have now

- One shared tracing library used by every HTTP service.
- A server span for every real request, named by route, with probes excluded.
- Environment-driven configuration: endpoint, sampling, batching, queue limits, timeout.
- Proof that tracing failures can't hurt requests.

Each service traces its own work, but the traces don't connect. In [Part 11](11-connect-traces-across-services.md) we pass trace context between services, over HTTP and through RabbitMQ, so one request becomes one trace.

## Key takeaways

- Instrument with OpenTelemetry so the services never depend on a tracing vendor.
- Keep tracing setup in one shared, explicit library; configure it with standard `OTEL_*` variables.
- Use a `parentbased_` sampler so all services in a request make the same keep-or-drop decision.
- `BatchSpanProcessor` keeps exporting off the request path; its queue size is tracing's memory ceiling.
- The Python OTLP exporter reads `OTEL_EXPORTER_OTLP_TIMEOUT` in seconds, not milliseconds.
- Exclude probe endpoints from tracing, and set tracing up after Gunicorn forks.

## FAQ

### How do I add OpenTelemetry tracing to a FastAPI app?

Create a `TracerProvider` with a `Resource` containing `service.name`, add a `BatchSpanProcessor` with an `OTLPSpanExporter`, register it with `trace.set_tracer_provider()`, then call `FastAPIInstrumentor.instrument_app(app)`. Configure the exporter's endpoint with `OTEL_EXPORTER_OTLP_ENDPOINT`.

### What is the difference between OpenTelemetry auto and manual instrumentation?

Zero-code (auto) instrumentation patches supported libraries at start-up via the `opentelemetry-instrument` command, configured by environment variables. Manual (explicit) instrumentation sets up the SDK and chooses instrumentations in code. Auto is fastest to start; explicit gives more control, for example over excluded URLs, and works the same for web apps and plain worker processes.

### Which OpenTelemetry sampler should I use?

Use a parent-based sampler so downstream services follow the first service's decision. Locally, `parentbased_always_on` records everything. In production, `parentbased_traceidratio` with `OTEL_TRACES_SAMPLER_ARG=0.1` keeps about 10%. For keeping all errors while sampling the rest, use tail sampling in a collector.

### Is OTEL_EXPORTER_OTLP_TIMEOUT in seconds or milliseconds?

The OpenTelemetry specification says milliseconds, but the Python OTLP exporter reads it as seconds (default `10`). Check your SDK's documentation; in Python, `10` means ten seconds.

### Does OpenTelemetry work with Gunicorn?

Yes, but set up tracing in each worker after it forks, because the background export thread doesn't survive `fork()`. Without `--preload`, Gunicorn imports the app in each worker, so module-level setup works. With `--preload`, initialise tracing in a `post_fork` hook.

---

**Series navigation:** Previous: [Part 9, Store Traces in Tempo](09-store-traces-in-tempo.md) · [Series index](README.md) · Next: [Part 11, Connect Traces Across Services and Queues](11-connect-traces-across-services.md)
