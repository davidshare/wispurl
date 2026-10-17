---
title: "Observability for WispURL, Part 2: Expose RED Metrics from the Services"
seo_title: "RED Metrics in FastAPI with Prometheus and Gunicorn"
slug: red-metrics-fastapi-prometheus-gunicorn
description: "Add RED metrics to FastAPI services with a shared Prometheus middleware, avoid label cardinality explosions, and fix wrong counters under Gunicorn workers."
series: "Observability for WispURL"
part: 2
date: 2026-10-17
last_updated: 2026-10-17
author: David Essien
tags: [prometheus, metrics, python, fastapi, gunicorn, red-method]
keywords:
  - "RED metrics"
  - "FastAPI Prometheus middleware"
  - "prometheus_client multiprocess"
  - "Gunicorn Prometheus metrics"
  - "Prometheus label cardinality"
  - "Prometheus histogram vs summary"
  - "histogram buckets"
difficulty: intermediate
estimated_time: 45 minutes
prerequisites:
  - "Part 1: Start the Stack with Prometheus"
repo_files:
  - shared/wispurl_metrics/src/wispurl_metrics/prometheus.py
  - shared/wispurl_metrics/src/wispurl_metrics/gunicorn_hooks.py
  - gateway/entrypoint.sh (and the other five HTTP services)
  - gateway/app/main.py (and the other five HTTP services)
  - docker-compose.yml
---

# Observability for WispURL, Part 2: Expose RED Metrics from the Services

> **In short:** to expose RED metrics (rate, errors, duration) from FastAPI services, use one shared Prometheus middleware with a request counter, a latency histogram and an in-progress gauge. Label requests by **route template** read *after* routing, never by raw URL, to avoid a cardinality explosion. When Gunicorn runs several workers, enable `prometheus_client` multiprocess mode (`PROMETHEUS_MULTIPROC_DIR`, a clean directory at start, and a `child_exit` hook) or every scrape sees only one worker's numbers.

Prometheus is running, but it has nothing from WispURL to store. Before we can collect metrics, the services have to **produce** them. In this part you will:

1. decide which metrics every HTTP service should expose, and why;
2. build them into one shared library so all services report the same way;
3. avoid the most common way to crash Prometheus: unbounded labels;
4. make the numbers correct when Gunicorn runs several worker processes;
5. wire it into a service and check the output.

This is the only part of the metrics story that touches application code. Everything after it is configuration.

## What to measure: the RED method

You could measure hundreds of things. A good starting point for any request-driven service is the **RED method**:

| Letter | Measures | Question | Our metric |
| --- | --- | --- | --- |
| **R**ate | Requests per second | How busy is it? | `http_requests_total` (a counter) |
| **E**rrors | Failed requests per second | Is it working? | the same counter, filtered by `status=~"5.."` |
| **D**uration | How long requests take | Is it fast enough? | `http_request_duration_seconds` (a histogram) |

These three describe a service from the **user's point of view**. If rate, errors and duration all look normal, users are almost certainly fine, whatever the CPU graph says. That's why RED metrics are what we alert on and what the main dashboard shows.

Its partner, the **USE method** (Utilization, Saturation, Errors), describes *resources* like CPU, memory and disks. We'll add those in Part 5. A simple rule of thumb: RED for services, USE for the machines and dependencies under them.

We add one more metric, `http_requests_in_progress`. It counts requests currently being handled, which is an early sign of **saturation**: if it climbs, the service is falling behind.

## Design decisions

### One shared library, not code in every service

WispURL has six HTTP services. If each one defined its own metrics, they would drift apart: different names, different labels, different buckets. Dashboards and alerts would then need special cases for each service.

So the metrics live in one small package, `shared/wispurl_metrics`, that every service installs. Each service adds two lines to use it. Changing a metric means changing one file.

### Middleware, not code in every route

The library is an HTTP **middleware**: code that runs around every request. It sees the method, the matched route, the status code and the timing for every request, without anyone remembering to add a line to each new route.

### The metric types, and why a histogram

Prometheus has four metric types. We use three:

| Type | Behaviour | Use it for | Ours |
| --- | --- | --- | --- |
| **Counter** | Only goes up (resets to 0 on restart) | Things that happen: requests, errors | `http_requests_total` |
| **Gauge** | Goes up and down | Things that are: queue length, requests in flight | `http_requests_in_progress` |
| **Histogram** | Counts observations into buckets (`≤ 5 ms`, `≤ 10 ms`, …) | Durations and sizes, when you need percentiles | `http_request_duration_seconds` |
| Summary | Calculates percentiles inside the service | Rarely the right choice | — |

Why a histogram and not a summary for latency? A summary calculates the 95th percentile inside each process, and **you can't average percentiles**. With six gateway workers, the p95 of each worker tells you nothing reliable about the p95 of the service. A histogram only stores bucket counts, and counts *can* be added up across processes and containers. Prometheus then calculates the percentile from the combined buckets with `histogram_quantile()`.

### Choosing histogram buckets

A histogram's accuracy depends on its buckets. Prometheus can only tell you "the p95 is somewhere between 250 ms and 500 ms" if those are neighbouring buckets. We use:

```text
5ms 10ms 25ms 50ms 100ms 250ms 500ms 1s 2.5s 5s 10s
```

The reasoning:

- **Dense where it matters.** A redirect should take a few milliseconds; most API calls well under 250 ms. That's where most buckets are.
- **One bucket at each alert threshold.** Our latency alert fires when p95 is over 1 second (Part 15), so there's a bucket edge at exactly `1.0`.
- **A ceiling.** Requests time out around 30 seconds at the gateway. Anything over 10 seconds is simply "far too slow", and finer detail there wouldn't change any decision.
- **Not too many.** Every bucket is a separate time series for every label combination. Eleven buckets is a reasonable balance.

### Naming

Prometheus has naming conventions, and following them makes your metrics instantly readable to anyone who knows Prometheus:

- counters end in `_total` (`http_requests_total`);
- use base units in the name: `_seconds` not `_ms`, `_bytes` not `_kb`;
- the subject comes first (`http_request_...`), so related metrics sort together.

## The label trap: cardinality

This is the most important idea in this part.

Every unique combination of label values is a separate **time series**, and Prometheus keeps every active series in memory. The number of combinations is called **cardinality**. Our request counter has four labels:

```text
http_requests_total{service, method, path, status}
```

If `path` is the **raw URL**, then every short link becomes a new series:

```text
http_requests_total{path="/Iq4wPsS", ...}
http_requests_total{path="/3JaFOUq", ...}
http_requests_total{path="/x9Kd02a", ...}   ← one per short code, forever
```

A URL shortener has millions of short codes. Bots that scan for `/wp-admin`, `/.env` and thousands of other random paths make it worse. Memory grows until Prometheus is killed.

The fix is to label by the **route template**, the pattern the route was declared with:

```text
http_requests_total{path="/{short_code}", ...}   ← one series, however many links exist
```

Requests that match no route at all (404s from scanners) get one fixed label, `<unmatched>`, so they can't create series either.

There's a subtle catch. In FastAPI (Starlette), the matched route is only known **after** the router has run. Middleware code that runs *before* the request is handled sees no route yet. A middleware that reads the route at the start of the request, and falls back to the raw URL when there's none, will **always** fall back. That quietly produces the explosion above. The route must be read *after* the request has been processed.

Rules for labels, which apply to every metric you ever write:

- **Good labels** have a small, fixed set of values: service name, HTTP method, status code, route template, queue name.
- **Never use** user IDs, emails, short codes, raw URLs, request IDs, trace IDs or timestamps as labels. Those belong in logs and traces.

## Step 1: The metrics library

The library is `shared/wispurl_metrics/src/wispurl_metrics/prometheus.py`. Its first part defines the three metrics:

```python
UNMATCHED_PATH = "<unmatched>"

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["service", "method", "path", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["service", "method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

REQUESTS_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "HTTP requests currently being processed",
    ["service", "method"],
    multiprocess_mode="livesum",
)
```

> `prometheus.py` lines 17–42.

Notice that the in-progress gauge has **no `path` label**. It has to go up when a request *starts*, before routing has happened, so the route template isn't known yet. The `multiprocess_mode="livesum"` argument is explained in Step 3.

The middleware does the measuring:

```python
class PrometheusMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, service_name: str):
        super().__init__(app)
        self.service_name = service_name

    async def dispatch(self, request: Request, call_next):
        method = request.method
        in_progress = REQUESTS_IN_PROGRESS.labels(
            service=self.service_name,
            method=method,
        )
        in_progress.inc()

        start = time.perf_counter()
        response = None

        try:
            response = await call_next(request)
            return response
        finally:
            duration = time.perf_counter() - start
            # Default to "500" if an exception occurred and no response was generated
            status = str(response.status_code) if response else "500"

            # Routing has run by now, so the route template (e.g. /links/{short_code})
            # is known. Labelling by template, not raw URL, keeps cardinality bounded.
            route = request.scope.get("route")
            path = getattr(route, "path", UNMATCHED_PATH)

            REQUEST_COUNT.labels(
                service=self.service_name, method=method, path=path, status=status,
            ).inc()
            REQUEST_LATENCY.labels(
                service=self.service_name, method=method, path=path,
            ).observe(duration)
            in_progress.dec()
```

> `prometheus.py` lines 45–88.

Walking through it:

1. **Before the request:** increment the in-progress gauge and start a timer. `time.perf_counter()` is a monotonic clock, so it isn't affected if the system clock changes mid-request.
2. **`call_next(request)`** runs the rest of the app: routing, the handler, everything.
3. **`finally`** runs whether the handler returned normally or raised an exception. That guarantees the gauge always comes back down and failed requests are still counted.
4. If an exception escaped and there's no response, the request is counted as `500`, which is what the client will receive.
5. **Only now** do we read `request.scope["route"]`. The router has filled it in, so `route.path` is the template, such as `/{short_code}`. If no route matched, we use `<unmatched>`.

## Step 2: The `/metrics` endpoint

Prometheus needs a page to scrape. The library provides it:

```python
def metrics_endpoint(request: Request) -> Response:
    if os.environ.get("PROMETHEUS_MULTIPROC_DIR"):
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
    else:
        registry = REGISTRY
    return Response(
        content=generate_latest(registry),
        media_type=CONTENT_TYPE_LATEST,
    )
```

> `prometheus.py` lines 91–104.

`generate_latest` renders every metric in Prometheus's text format. The `if` branch handles multiple worker processes, which is the next step.

## Step 3: Make the numbers correct with several workers

Each WispURL HTTP service runs under **Gunicorn** with two worker processes (`WEB_CONCURRENCY=2`). Gunicorn starts several copies of the app so one container can use more than one CPU core.

That causes a problem for metrics. Each worker is a separate process with **its own counters in its own memory**. When Prometheus scrapes `/metrics`, whichever worker happens to receive that request answers with *its* numbers only:

```text
scrape 1 → answered by worker A → http_requests_total 512
scrape 2 → answered by worker B → http_requests_total 488   ← "went down"?
scrape 3 → answered by worker A → http_requests_total 530
```

A counter that appears to go down is treated as a restart, so `rate()` produces nonsense spikes, and you only ever see about half the traffic.

There are two ways to fix it:

| Option | How | Trade-off |
| --- | --- | --- |
| **One worker per container** | `WEB_CONCURRENCY=1`, run more containers | Simplest and the most "container-native". But you need more containers for the same throughput, and each one has its own memory overhead. |
| **Multiprocess mode** | Workers write metrics to shared files; `/metrics` adds them up | Keeps the existing process model. Needs a shared directory and a little setup. |

We use **multiprocess mode** because it doesn't change how the services are deployed. In Kubernetes later, the one-worker approach becomes attractive because the platform handles scaling. Either is a valid decision; just make sure you make one, because the default is silently wrong.

Multiprocess mode needs three things.

### 3a. A directory, set by an environment variable

`prometheus_client` switches to multiprocess mode when `PROMETHEUS_MULTIPROC_DIR` is set. Each worker then writes its values to small files in that directory, and the `/metrics` code from Step 2 reads and combines all of them.

Add the variable to each of the six HTTP services in `docker-compose.yml`, in their `environment:` block:

```yaml
      # Gunicorn runs several workers; aggregate their metrics (see entrypoint.sh).
      PROMETHEUS_MULTIPROC_DIR: /tmp/prometheus-multiproc
```

> For example `docker-compose.yml` lines 117–118 (auth-service).

Only the Gunicorn services get it. The queue workers (analytics consumer, cleanup, notification) run as single processes and don't serve `/metrics`.

### 3b. Start with an empty directory

If the container restarts, files from the previous run would still be in the directory and would be added to the new totals. Each service's entrypoint therefore clears it before starting Gunicorn:

```sh
# Prometheus multiprocess mode: each Gunicorn worker writes its metrics to this
# directory and /metrics sums them. Start empty so a previous run isn't counted.
if [ -n "${PROMETHEUS_MULTIPROC_DIR:-}" ]; then
  rm -rf "$PROMETHEUS_MULTIPROC_DIR"
  mkdir -p "$PROMETHEUS_MULTIPROC_DIR"
fi
```

> `gateway/entrypoint.sh` lines 4–9 (the same block is in all six HTTP services).

### 3c. Tell Prometheus when a worker dies

Counters and histograms are fine to keep after a worker exits: those requests really did happen. **Gauges** are different. If a worker dies while it's handling three requests, its in-progress gauge would stay at 3 forever.

That's what `multiprocess_mode="livesum"` on the gauge is for: "sum this gauge across **live** processes only". For that to work, `prometheus_client` has to be told when a process dies. Gunicorn has a hook for exactly that moment, `child_exit`, and the library ships it:

```python
from prometheus_client import multiprocess


def child_exit(server: Any, worker: Any) -> None:
    """Drop a dead worker's live gauge values so they stop counting toward livesum."""
    multiprocess.mark_process_dead(worker.pid)
```

> `shared/wispurl_metrics/src/wispurl_metrics/gunicorn_hooks.py` lines 8–13.

Gunicorn loads it with `-c python:<module>`, which reads Gunicorn settings and hooks from a Python module. The entrypoint's start command becomes:

```sh
exec gunicorn app.main:app \
  -c python:wispurl_metrics.gunicorn_hooks \
  -k uvicorn.workers.UvicornWorker \
  --workers "${WEB_CONCURRENCY:-2}" \
  --bind "0.0.0.0:${PORT:-8000}"
```

> `gateway/entrypoint.sh` lines 12–16.

Because the hook lives in the shared library, every service gets it from the same place, with no per-service Gunicorn config file.

## Step 4: Wire it into a service

Each service needs two things in its FastAPI setup (`app/main.py`): the middleware and the endpoint. In the gateway:

```python
from wispurl_metrics import PrometheusMiddleware, metrics_endpoint

# inside create_app():
    app.add_middleware(PrometheusMiddleware, service_name="gateway")

    @app.get("/metrics")
    def expose_metrics(request: Request) -> Response:
        return metrics_endpoint(request)
```

> `gateway/app/main.py` lines 22, 165 and 171–173.

**Use the Compose service name as `service_name`.** The other services use `auth-service`, `shortener-service`, `analytics-service`, `qr-service` and `rate-limiter-service`. This looks like a small detail, but it's a design decision with consequences: in later parts, logs are labelled with the Compose service name and traces with `OTEL_SERVICE_NAME`, which is also the Compose name. When all three signals use the *same* name for a service, a dashboard can show a service's metrics and logs side by side, and Grafana can jump from a trace to that service's logs. If metrics called it `shortener` while logs called it `shortener-service`, none of that would line up.

The library itself is a normal package. Each service lists it as a dependency in its `pyproject.toml` and points uv at the shared folder:

```toml
dependencies = [
    # ...
    "wispurl-metrics",
]

[tool.uv.sources]
wispurl-metrics = { path = "../shared/wispurl_metrics", editable = true }
```

The Docker build copies the `shared/` folder in through an additional build context (`additional_contexts: shared_lib: ./shared` in `docker-compose.yml`), so the package installs inside the image too.

## Step 5: Rebuild the services

The library and the entrypoints are baked into the images, so rebuild:

```sh
docker compose up --build -d
```

## Check that it works

The gateway's port is published on the host, so you can read its metrics page directly. First send it some traffic: open the app at http://localhost:3000, sign in and click a short link a few times, or use `curl http://localhost:8080/<a-short-code>`. Then:

```sh
curl -s http://localhost:8080/metrics | grep http_request_duration_seconds_count
```

You'll see one line per route, with route **templates**, not raw URLs:

```text
http_request_duration_seconds_count{method="GET",path="/health",service="gateway"} 161.0
http_request_duration_seconds_count{method="POST",path="/v1/auth/{path:path}",service="gateway"} 2.0
http_request_duration_seconds_count{method="POST",path="/v1/links",service="gateway"} 1.0
http_request_duration_seconds_count{method="GET",path="/{short_code}",service="gateway"} 13.0
```

Thirteen redirects to different short codes, one series: `path="/{short_code}"`.

**Check the cardinality protection.** Request a path that doesn't exist, then look for it:

```sh
curl -s -o /dev/null http://localhost:8080/v1/this-does-not-exist
curl -s http://localhost:8080/metrics | grep 'status="404"'
```

The 404 is counted under `path="<unmatched>"` (or under a catch-all route template, if one matched), never under the raw path you typed.

**Check the worker aggregation.** Scrape several times in a row and compare a counter:

```sh
for i in 1 2 3 4 5; do
  curl -s http://localhost:8080/metrics | grep 'http_requests_total{method="GET",path="/{short_code}"'
done
```

Every line shows the same number. Without multiprocess mode, the numbers would jump between two values as different workers answered.

**Look inside the multiprocess directory.** Each worker writes its own files:

```sh
docker compose exec gateway ls /tmp/prometheus-multiproc
```

```text
counter_9.db  counter_10.db  gauge_livesum_9.db  gauge_livesum_10.db  histogram_9.db  histogram_10.db
```

The numbers are the worker process IDs, so yours will differ. Two workers, two sets of files.

The other services aren't published on the host. To check one, run the request from inside the gateway container, which shares their network:

```sh
docker compose exec gateway python -c "import urllib.request; print(urllib.request.urlopen('http://shortener-service:8000/metrics').read().decode()[:600])"
```

## When something goes wrong

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| A new series appears for every short code or URL | The route is read before routing has run | Read `request.scope["route"]` after `call_next`, as in Step 1. |
| Counters jump up and down between scrapes | Several Gunicorn workers without multiprocess mode | Set `PROMETHEUS_MULTIPROC_DIR` and rebuild. |
| `/metrics` returns empty or errors after setting the variable | The directory doesn't exist or isn't writable | Make sure the entrypoint creates it (Step 3b). `/tmp` is writable by the non-root `app` user. |
| `http_requests_in_progress` never returns to 0 | A dead worker's gauge is still counted | Load the `child_exit` hook with `-c python:wispurl_metrics.gunicorn_hooks`. |
| `ModuleNotFoundError: wispurl_metrics` at startup | The service doesn't depend on the library | Add it to `pyproject.toml` and `[tool.uv.sources]`, run `uv lock`, rebuild. |


## What you have now

Every HTTP service exposes the same RED metrics on `/metrics`:

- `http_requests_total` by service, method, route template and status;
- `http_request_duration_seconds` as a histogram, ready for percentiles;
- `http_requests_in_progress` as a saturation signal.

Labels are bounded, the numbers are correct across Gunicorn workers, and every service reports under its Compose name.

Nothing is collecting them yet. In [Part 3](03-collect-service-metrics-with-alloy.md) we deploy Grafana Alloy to find the services automatically, scrape them, and push the results into Prometheus.

## Key takeaways

- RED (rate, errors, duration) describes a service from the user's side; it's what you alert on.
- Use a histogram, not a summary, for latency: bucket counts can be added across processes, percentiles can't.
- Put a bucket edge at every latency threshold you alert on.
- Label by route template, read after routing has run. Raw URLs, IDs and short codes as labels will eventually take Prometheus down.
- Multiple Gunicorn workers need multiprocess mode, or counters jump between scrapes and you see only part of the traffic.
- Use the same service name in metrics, logs and traces so the signals can be linked later.

## FAQ

### What are RED metrics?

RED stands for Rate (requests per second), Errors (failed requests per second) and Duration (how long requests take). Together they describe a request-driven service from the user's point of view, which makes them the right basis for dashboards and alerts.

### Should I use a Prometheus histogram or summary for latency?

Use a histogram. A summary calculates percentiles inside each process, and percentiles from several processes or containers can't be combined. A histogram stores bucket counts, which add up correctly, and Prometheus calculates percentiles across all instances with `histogram_quantile()`.

### What is label cardinality in Prometheus and why does it matter?

Cardinality is the number of unique label-value combinations for a metric. Each combination is a separate time series held in memory. Labels with unbounded values, such as user IDs or raw URL paths, create an ever-growing number of series and can exhaust Prometheus's memory. Keep labels to small, fixed sets of values.

### Why do my Prometheus counters jump around with Gunicorn?

Each Gunicorn worker is a separate process with its own counters, and each scrape is answered by whichever worker receives it. Set `PROMETHEUS_MULTIPROC_DIR` so workers write to shared files and `/metrics` combines them, clear that directory at startup, and mark dead workers with a `child_exit` hook. Alternatively, run one worker per container.

### How do I get the route template in FastAPI middleware?

Read `request.scope["route"].path` after calling `call_next(request)`. Starlette fills in the matched route during routing, which happens after middleware starts, so reading it earlier always finds nothing.

---

**Series navigation:** Previous: [Part 1, Start the Stack with Prometheus](01-start-the-stack-with-prometheus.md) · [Series index](README.md) · Next: [Part 3, Collect Service Metrics with Grafana Alloy](03-collect-service-metrics-with-alloy.md)
