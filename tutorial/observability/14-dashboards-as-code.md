---
title: "Observability for WispURL, Part 14: Production Dashboards as Code"
seo_title: "Production Grafana Dashboards as Code with Python: Overview, Service Drill-Down, Business and Infrastructure"
slug: grafana-production-dashboards-as-code
description: "Design a production-style set of Grafana dashboards: a system overview, per-service drill-down, worker and queue views, business KPIs, infrastructure and the monitoring stack itself. Generate them from one Python script, provision them into folders and keep them in Git."
series: "Observability for WispURL"
part: 14
date: 2026-10-17
last_updated: 2026-10-19
author: David Essien
tags: [grafana, dashboards, provisioning, promql, red-method, use-method, business-metrics, prometheus-client]
keywords:
  - "Grafana dashboards as code"
  - "generate Grafana dashboards with Python"
  - "Grafana dashboard provisioning folders"
  - "foldersFromFilesStructure"
  - "per-service Grafana dashboard template variables"
  - "Grafana data links drill-down"
  - "business metrics Prometheus"
  - "RabbitMQ consumer metrics dashboard"
  - "RED and USE dashboards"
difficulty: intermediate
estimated_time: 75 minutes
prerequisites:
  - "Part 13: Link Logs and Traces"
repo_files:
  - shared/wispurl_metrics/src/wispurl_metrics/business.py
  - shared/wispurl_metrics/src/wispurl_metrics/__init__.py
  - shortener-service/shared/messaging.py
  - docker-compose.yml
  - observability/grafana/generate_dashboards.py
  - observability/grafana/provisioning/dashboards/dashboards.yaml
  - observability/grafana/dashboards/
---

# Observability for WispURL, Part 14: Production Dashboards as Code

> **In short:** build dashboards in layers. A **System Overview** says whether anything is broken. **Service Detail** and **Workers & Messaging** let you pick one service, worker or queue and see everything about it. A **Business** dashboard shows what the product is doing, and **Infrastructure** and **Observability** folders cover the dependencies and the monitoring stack. To feed them, add low-cardinality business and messaging counters to the code and give the background workers a `/metrics` endpoint. Then generate all 14 dashboards from one standard-library Python script, and let Grafana load them from Git into one folder per directory (`foldersFromFilesStructure: true`).

You've been exploring with ad-hoc queries since Part 6. During an incident nobody wants to type PromQL from memory, and "the dashboards" quickly becomes the thing people trust or ignore. This part builds a set of dashboards that works like the ones production teams use. It starts with one screen that answers "is something wrong?", and every number on it is a link to the screen that answers "why?".

## What a production dashboard set needs

A first attempt at dashboards is usually two pages: one for request metrics (RED) and one for resources (USE). That's a good start, and it quickly shows its limits:

- **You can't focus on one service.** Ten services on one graph is noise. When the shortener is slow, you want a page about the shortener: its routes, its database calls, its logs, its container.
- **Applications and infrastructure are mixed together.** The person checking whether Postgres is healthy and the person checking whether redirects are slow need different pages.
- **Background work is invisible.** The analytics consumer, the cleanup job and the notification sender have no HTTP traffic, so request metrics never show them. If the click pipeline stops, no RED panel moves.
- **Nothing shows what the product is doing.** "200 requests per second" doesn't tell you whether people are signing up, creating links, or hitting dead links. Those are the numbers a product owner, and often an on-call engineer, actually cares about.
- **The monitoring stack monitors everything except itself.** If Loki drops log lines or Alloy stops sending metrics, every other dashboard quietly lies.

So the set we build has four layers, one Grafana folder each:

| Folder | Dashboard | The question it answers |
| --- | --- | --- |
| **Overview** | WispURL — System Overview | Is anything broken right now, and where should I look? |
| | WispURL — Business | What is the product doing: accounts, links, redirects, clicks, notifications? |
| **Applications** | Service Detail | Everything about one HTTP service (pick it from a drop-down) |
| | Workers & Messaging | Queues, consumers, retries, dead letters, and each background worker |
| **Infrastructure** | Docker Host | Is the machine running out of CPU, memory, disk or I/O? |
| | Containers | Which container is using the resources? |
| | PostgreSQL | Connections, transactions, cache hit ratio, locks, per-database size |
| | Redis | Clients, commands, memory, keys, evictions |
| | RabbitMQ | Queues, message rates, connections, channels, node resources |
| **Observability** | Prometheus | Is the metrics store healthy: ingestion, series, rule evaluation, remote write? |
| | Loki | Are logs arriving, and are any being refused? |
| | Tempo | Are traces arriving, and are queries fast? |
| | Alloy | Is the collector scraping, tailing logs and forwarding everything? |
| | Alerting | What is firing, and are notifications going out? |

## Design decisions

### Drill down from overview to detail

Teams that run large systems design dashboards as a hierarchy rather than a pile. The top level has very few numbers, each with a colour threshold, so you can read it from across the room. Every one of those numbers is a **link** to the next level down, which already has the right service or queue selected. From there, trace and log panels take you to the individual request.

In practice an investigation goes like this:

1. **Overview:** "Gateway 5xx ratio is red." Click the *Service health* table row for the failing service.
2. **Service Detail**, already filtered to that service: *5xx per second by route* shows the endpoint, the *Dependencies* row shows whether a database call got slower, and the *Failed requests* panel lists traces.
3. Click a trace ID and the trace opens in Tempo. From there, *Logs for this span* (Part 13) shows what the code logged.

You never type a query, and you never lose the time range, because every link carries it.

### One dashboard per kind of thing, not per instance

There is one **Service Detail** dashboard with a `$service` drop-down, not six copies of a service dashboard. Grafana template variables make one page serve every service, and new services appear in the drop-down by themselves. That only works because every signal uses the same label values: metrics, logs and traces all say `service="shortener-service"` (Parts 2, 8 and 10). Consistent labels are what make a drill-down possible.

### Folders by audience

Folders split the dashboards by who is looking and why. An application developer lives in *Applications*. Someone tuning Postgres goes to *Infrastructure*. The person who runs the monitoring stack opens *Observability*. *Overview* is for everyone. Every dashboard also has two drop-down menus in its top bar, **All WispURL dashboards** and one for its own folder, so moving sideways is one click.

### Methods for each layer

Each layer uses the method that fits it:

- **Services: RED** (rate, errors, duration) per service and per route, plus *in progress* as the saturation signal.
- **Resources: USE** (utilisation, saturation, errors) for the host, containers, Postgres connections and Redis memory.
- **Queues:** depth, consumers, processing outcome (ack, retry, dead letter) and processing time. For a queue, these are the RED and USE signals.
- **Business: counts and ratios of product events.** Totals over the selected range ("links created today") and ratios that reveal problems ("share of redirects that found a link").

### Business metrics, without exploding cardinality

Business metrics are the easiest place to hurt Prometheus. The tempting label is the one that answers the product question directly: `short_code`, `user_id`, `email`, `url`. Every distinct value creates a new time series, forever, so a million links means a million series. That is how a metrics store runs out of memory.

The rule in this project: **labels only take values from a small, fixed set.** `result="found|not_found|inactive|expired"`, `slug="custom|generated"`, `size="small|medium|large"`. Questions about individual links or users go to the analytics database, which is built for them. Prometheus answers "how many, how fast, how often does it fail".

### Generate the dashboards instead of hand-editing JSON

Fourteen dashboards with about 200 panels share a lot: the same units, colour thresholds, error-ratio query, latency percentiles, data source UIDs and link format. Copy-pasted JSON drifts. One dashboard gets the threshold fix and the others don't. So the dashboards are **generated** from one Python script, `observability/grafana/generate_dashboards.py`. A change made once there applies everywhere.

Why a plain Python script rather than one of the established tools?

| Option | Trade-off |
| --- | --- |
| Hand-written JSON | Fine for two dashboards; drifts badly at fourteen |
| Grafonnet (Jsonnet) | Mature, but a new language and toolchain for most teams |
| Grafana Foundation SDK | Typed builders in Go, TypeScript, Python, Java; an extra dependency that tracks Grafana's schema |
| Terraform Grafana provider | Good when Terraform already manages Grafana; it needs a running Grafana and a state file |
| **Standard-library Python** | Nothing to install, readable by anyone who reads Python, and its output is ordinary dashboard JSON |

The script uses only the standard library. Anyone can run it on a fresh machine, and a CI job can run it later to check that the committed JSON is up to date. The generated JSON is committed too, so Grafana doesn't need Python and a reviewer can see exactly what changed. If the panel builders ever grow complicated, the Foundation SDK is the natural next step, and the dashboard design stays the same.

### Git stays the source of truth

As in Part 6, dashboards are **provisioned**. Grafana loads them from files and refuses to save changes made in the UI. That prevents the classic failure where someone "quickly fixes" a panel in production and the fix is lost or silently differs from Git.

## Step 1: Add business and messaging metrics

Dashboards can only show what the code measures. Part 2 gave every HTTP service request metrics. Now we add the product's own events. They go in the shared metrics package next to the HTTP metrics, in a new module: `shared/wispurl_metrics/src/wispurl_metrics/business.py`.

The module starts by stating its rules, so the next person adding a metric follows them:

```python
"""Business and messaging metrics for WispURL.

HTTP metrics (prometheus.py) say how the services behave; these say what the
product is doing: signups, links, redirects, clicks, notifications, and how the
event pipeline between services is coping.

Rules for every metric here:
- labels only take values from small, fixed sets (never user IDs, emails, short
  codes or URLs);
- every metric has at least one label, so a service that imports this module
  but never uses a metric doesn't export meaningless zero series.
"""
```

> `business.py` lines 1–12.

The second rule exists because of how `prometheus_client` behaves. A counter **without** labels is exported as `0` by every process that imports the module. The QR service would export `wispurl_links_created_total 0`, and that looks like "the QR service created zero links". A counter **with** labels exports nothing until a label combination is used, so each service only exports what it actually does.

The metrics, and where each one is recorded:

| Metric | Labels (all bounded) | Recorded by |
| --- | --- | --- |
| `wispurl_auth_events_total` | `action` (signup, login, refresh, logout), `result` (success, duplicate_email, weak_password, invalid_credentials, inactive_user, invalid_token, rate_limited, rejected) | auth-service routes |
| `wispurl_links_created_total` | `slug` (custom, generated), `expiry` (yes, no) | shortener links route |
| `wispurl_link_create_rejections_total` | `reason` (rate_limited, duplicate_slug, invalid_slug, exhausted) | shortener links route |
| `wispurl_links_deleted_total` | `result` (deleted, not_found) | shortener links route |
| `wispurl_redirects_total` | `result` (found, not_found, inactive, expired) | shortener `resolve_link` |
| `wispurl_rate_limiter_unavailable_total` | `fallback` (allowed, denied) | shortener rate-limit client |
| `wispurl_rate_limit_decisions_total` | `action`, `decision` (allowed, denied) | rate-limiter-service |
| `wispurl_qr_codes_generated_total` | `size` (small, medium, large) | qr-service |
| `wispurl_clicks_recorded_total` | `source` (queue, http) | analytics consumer and API |
| `wispurl_link_milestones_total` | `threshold` (configured milestones) | analytics consumer |
| `wispurl_links_expired_total` | `source` (cleanup) | cleanup-service |
| `wispurl_cleanup_sweep_seconds` (histogram) | `outcome` (empty, deactivated, error) | cleanup-service |
| `wispurl_notifications_total` | `type`, `channel`, `result` (sent, failed, ignored) | notification-service |
| `wispurl_messages_published_total` | `routing_key`, `result` (ok, error) | shared messaging module |
| `wispurl_messages_processed_total` | `queue`, `result` (ack, retry, dead_letter, malformed) | shared messaging module |
| `wispurl_message_processing_seconds` (histogram) | `queue` | shared messaging module |

> `business.py` lines 14–128.

A few labels need a word of explanation:

- **QR `size`** is a band, not the pixel value. The API accepts any size, so `size="437"` would be unbounded. `qr_size_band()` (lines 131–137) maps it to small, medium or large.
- **`threshold`** comes from the configured milestone list (for example 100, 1000), so it's bounded by configuration.
- **`queue` and `routing_key`** come from the few queues and routing keys the code declares, never from message content.

### Recording the reason, not just the outcome

The most useful business metric is often hidden behind an error the user never sees in detail. Every failed short-link lookup returns the same 404, which is correct for the user. Operationally, though, "never existed", "owner deactivated it" and "expired" mean different things. The redirect path records the reason before raising the shared error:

```python
async def resolve_link(self, *, short_code: str) -> Link:
    # Callers always get LinkNotFoundError, but the metric records why.
    link = await self._links.get_by_short_code(short_code)
    if link is None:
        REDIRECTS.labels(result="not_found").inc()
        raise LinkNotFoundError
    if not link.is_active:
        REDIRECTS.labels(result="inactive").inc()
        raise LinkNotFoundError
    if link.expires_at is not None and link.expires_at <= datetime.now(UTC):
        REDIRECTS.labels(result="expired").inc()
        raise LinkNotFoundError
    REDIRECTS.labels(result="found").inc()
    return link
```

> `shortener-service/app/services/link_service.py` lines 95–108.

The other routes follow the same pattern: each route maps the domain exception to a `result` or `reason` label (for example `_REJECTIONS` in `shortener-service/app/routes/links.py` and `_RESULTS` in `auth-service/app/routes/auth.py`), records it, and re-raises so the HTTP response is unchanged.

### Instrument the message pipeline once

All producers and consumers share one messaging module (copied into each service's `shared/` folder). Instrumenting it once covers every queue. On the consumer side, each message ends in exactly one outcome, and a `finally` block records it together with the processing time:

```python
started = time.perf_counter()
result = "ack"
try:
    ...  # validate, handle, retry or dead-letter; each branch sets result
finally:
    # queue_name is one of a few declared queues, so the label is bounded.
    MESSAGES_PROCESSED.labels(queue=queue_name, result=result).inc()
    MESSAGE_PROCESSING_SECONDS.labels(queue=queue_name).observe(
        time.perf_counter() - started,
    )
```

> `shortener-service/shared/messaging.py` lines 274–319 (condensed; the full block sets `malformed`, `dead_letter` and `retry` in its branches).

`publish()` does the same with `wispurl_messages_published_total` (lines 153–183), counting `ok` or `error` per routing key. Together these give the click pipeline an end-to-end check: clicks **published** by the shortener should equal clicks **recorded** by the analytics consumer.

### Keep the package importable without a web framework

The metrics package's `__init__.py` used to import the HTTP middleware, which needs Starlette. The workers don't have Starlette installed, so importing `wispurl_metrics.business` from a worker would crash. The package now loads its HTTP pieces lazily, using a module-level `__getattr__` (PEP 562):

```python
def __getattr__(name: str) -> Any:
    if name in __all__:
        from . import prometheus

        return getattr(prometheus, name)
    raise AttributeError(f"module 'wispurl_metrics' has no attribute {name!r}")
```

> `shared/wispurl_metrics/src/wispurl_metrics/__init__.py` lines 18–23.

`from wispurl_metrics import PrometheusMiddleware` still works for the web services, and workers only ever load `business.py`. The cleanup service didn't depend on the package before, so `cleanup-service/pyproject.toml` now lists `wispurl-metrics` with the same local path source as the other services.

## Step 2: Give the workers a `/metrics` endpoint

The three background workers (analytics consumer, cleanup, notification) aren't web servers, so nothing exposed their metrics. `prometheus_client` ships a tiny HTTP server for exactly this case:

```python
def start_metrics_server(port: int = 8000) -> None:
    """Serve /metrics from a single-process worker (no web framework needed).

    For Gunicorn services use metrics_endpoint() instead: this exposes only the
    calling process's metrics.
    """
    start_http_server(port)
```

> `business.py` lines 140–146.

Each worker calls it at startup, for example `start_metrics_server(int(os.getenv("METRICS_PORT", "8000")))` at `analytics-service/app/worker.py` line 54, `cleanup-service/app/main.py` line 67 and `notification-service/app/main.py` line 34. The server runs in a background thread, so it doesn't interfere with the worker's event loop.

> **Why not use this in the web services too?** They run several Gunicorn worker processes. `start_http_server` only exposes the metrics of the process that called it, so you'd see one worker's share of the traffic. The web services keep using multiprocess mode and `metrics_endpoint()` from Part 2.

Then tell Alloy to scrape them. Part 3 discovers scrape targets from Docker labels, so each worker gets the same `prometheus-labels` anchor as the web services:

```yaml
    labels:
      # Workers serve /metrics on 8000 from a small built-in HTTP server.
      <<: [*prometheus-labels, *python-log-labels]
```

> `docker-compose.yml` lines 269–271 (analytics-consumer-service); the same at lines 320–322 (cleanup) and 373–375 (notification).

The endpoint also fixes a weak healthcheck. The workers' old check tested whether `/proc/1/status` existed, which is always true inside a running container. Now the check calls the metrics server:

```yaml
    healthcheck:
      # A real check: the worker's metrics server answers only while the process runs.
      test:
        [
          "CMD",
          "python",
          "-c",
          "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/metrics', timeout=2)",
        ]
```

> `docker-compose.yml` lines 298–306 (and 351–359, 400–408).

This proves the Python process is alive and answering. It does **not** prove the main loop is making progress, because the metrics thread keeps answering even if the consumer loop hangs. A heartbeat (the loop updates a timestamp, the check verifies it's recent) closes that gap and is tracked as a follow-up. Meanwhile the dashboards cover it: a stuck consumer shows as a growing queue with a flat *processed* line.

Rebuild and restart the application stack so the workers pick up the code and labels:

```sh
docker compose up -d --build analytics-consumer-service cleanup-service notification-service
```

## Step 3: Provision dashboards into folders

The provider file changes in one important way: the folder comes from the directory structure, not from a fixed `folder:` setting.

```yaml
apiVersion: 1

# Load the dashboard JSON files generated by observability/grafana/generate_dashboards.py.
# Each subdirectory of /var/lib/grafana/dashboards becomes a Grafana folder:
# Overview, Applications, Infrastructure and Observability. Dashboards live in
# Git; edits made in the UI are refused so the files stay the source of truth.
providers:
  - name: wispurl
    type: file
    disableDeletion: true
    allowUiUpdates: false
    updateIntervalSeconds: 30
    options:
      path: /var/lib/grafana/dashboards
      foldersFromFilesStructure: true
```

> `observability/grafana/provisioning/dashboards/dashboards.yaml` lines 1–15.

| Setting | Effect |
| --- | --- |
| `foldersFromFilesStructure: true` | `dashboards/Applications/wispurl-service.json` lands in a folder named **Applications**. The directory name is used as-is, which is why the directories are title-case. |
| `type: file`, `options.path` | Read JSON files from the directory Part 6 mounted read-only (`compose.observability.yaml` line 154) |
| `disableDeletion: true` | Dashboards can't be deleted from the UI |
| `allowUiUpdates: false` | Changes can't be saved from the UI |
| `updateIntervalSeconds: 30` | Changed files go live within 30 seconds, without a restart |

`foldersFromFilesStructure` can't be combined with a `folder:` value, so that line is gone.

## Step 4: The generator

`observability/grafana/generate_dashboards.py` has four parts. You don't need to read all 1,000 lines. The structure is what matters, because it's the part worth copying into your own projects.

### Panel builders

Each Grafana panel type has one function that takes the few things that change (title, queries, unit, description) and fills in everything else the same way every time:

| Builder | Lines | Used for |
| --- | --- | --- |
| `timeseries()` | 53–94 | Graphs; options for stacking, bars, thresholds, min/max |
| `stat()` | 96–126 | Single big numbers with colour thresholds and optional sparkline and links |
| `gauge()` | 128–146 | Percentages such as host CPU and Postgres connections |
| `table()` | 148–188 | Several queries joined on a label (the *Service health* table) |
| `heatmap()` | 190–206 | Latency distribution from histogram buckets |
| `logs()`, `log_volume()` | 208–224 | Loki log lines and lines per level |
| `traces()` | 226–234 | A TraceQL search shown as a table of traces |
| `link_to()` | 240–245 | A link to another dashboard that keeps the time range and can set a variable |

`link_to()` is what makes the drill-down work:

```python
def link_to(dashboard_uid: str, title: str, var: str | None = None, value: str = "${__value.raw}") -> dict:
    url = f"/d/{dashboard_uid}?${{__url_time_range}}"
    if var:
        url += f"&var-{var}={value}"
    return {"title": title, "url": url}
```

> `generate_dashboards.py` lines 240–245.

`${__url_time_range}` carries the current time range into the link, `var-service=` sets the target dashboard's drop-down, and `${__value.raw}` is the value that was clicked, for example the service name in a table row.

### Layout

Grafana places panels on a grid 24 columns wide. Calculating `x` and `y` by hand for 200 panels is tedious and error-prone, so a small `Layout` class does it:

```python
L = Layout()
L.row("Traffic")
L.add([
    (timeseries("Requests per second by route", [...], "reqps", stack=True), 12),
    (timeseries("Responses by status", [...], "reqps", stack=True), 12),
])
```

> `Layout` is at lines 252–275; this is the *Traffic* row of Service Detail (lines 532–536, condensed).

`row()` adds a heading and `add()` places panels left to right with the given widths. Adding a panel in the middle of a dashboard no longer means renumbering everything below it.

### Variables and the dashboard wrapper

`query_var()` (lines 283–300) builds a drop-down filled from a PromQL `label_values(...)` query. `custom_var()` (lines 303–316) builds one from a fixed list, such as log levels. `dashboard()` (lines 322–340) wraps a layout with the settings every dashboard shares:

- a fixed `uid`, so URLs in runbooks and alerts never break;
- tags `wispurl` and `wispurl-<folder>`, used by the two navigation drop-downs (Grafana's *dashboards* link type lists every dashboard with a given tag, so new dashboards appear in the menus automatically);
- a shared crosshair (`graphTooltip: 1`), so hovering over one graph highlights the same moment on all of them;
- `editable: false`, a 30-second refresh, and a default time range (6 hours, or 24 hours for Business).

### Shared queries

The queries that appear everywhere are defined once:

```python
def err_ratio(sel: str, by: str = "") -> str:
    group = f" by ({by})" if by else ""
    return f"(sum{group} (rate(http_requests_total{{{sel},{FAILED}}}[{RI}])) or sum{group} (rate(http_requests_total{{{sel}}}[{RI}])) * 0) / sum{group} (rate(http_requests_total{{{sel}}}[{RI}]))"


def quantile(q: float, metric: str, sel: str, by: str = "") -> str:
    group = f"{by}, le" if by else "le"
    return f"histogram_quantile({q}, sum by ({group}) (rate({metric}_bucket{{{sel}}}[{RI}])))"


def total(metric: str, sel: str = "") -> str:
    return f"sum(increase({metric}{{{sel}}}[{RANGE}])) or vector(0)"
```

> `generate_dashboards.py` lines 357–369.

Two details are worth understanding, because they fix the most common complaint about dashboards, "No data" when the answer is actually zero:

- **`err_ratio`** adds `or <all requests> * 0`. If nothing has failed, the 5xx series doesn't exist and the division returns nothing, so the panel says "No data". With the fallback, the ratio is a real `0`, shown in green.
- **`total`** ends with `or vector(0)` for the same reason, and uses `increase(...[$__range])`, so a stat shows the total for whatever time range is selected: "links created in the last 24 hours" or "this week", by changing the time picker.

### Writing the files

`main()` (lines 1029–1041) deletes the previous output, builds each dashboard listed in `ALL` (line 1026) and writes it to `dashboards/<Folder>/<uid>.json`. Starting from a clean directory means a dashboard removed from the script doesn't linger in Grafana.

## Step 5: What each dashboard shows

### System Overview (start here)

`overview()`, lines 376–437:

- **Health right now:** services up, services missing (the same check as the `ServiceDisappeared` alert), firing alerts, gateway requests per second, gateway 5xx ratio, gateway p95 latency, and the dead-letter queue. Each has a threshold colour, so the row is green, orange or red at a glance.
- **Services:** a *Service health* table with one row per service (instances up, requests per second, 5xx ratio, p95 latency). Clicking a service opens its Service Detail page. Below it are rate, error ratio and p95 by service over time.
- **Business over the selected time range:** new accounts, links created, redirects, clicks, QR codes, notifications. Each links to the Business dashboard.
- **Infrastructure:** host CPU, memory and disk gauges, Postgres connection usage, Redis up, and messages waiting in RabbitMQ. Each links to its dashboard.

### Service Detail

`service_detail()`, lines 514–604. Variables: **Service**, **Route** (multi-select, filled from the chosen service's routes) and **Log level**.

| Row | What you learn |
| --- | --- |
| Golden signals | Instances, requests/s, 5xx and 4xx ratios, p50/p95/p99, requests in progress |
| Traffic | Requests per route and responses by status |
| Errors | 5xx and 4xx per route, error ratio against the alert threshold |
| Latency | Percentiles, p95 per route, and a heatmap of the latency distribution |
| Dependencies (from traces) | Every SQL statement, Redis command and outgoing HTTP call this service makes, with p95 duration, from Tempo's span metrics; and which services or stores it calls, from the service graph (Parts 9 and 11) |
| Business events | Every `wispurl_*` counter this service exports |
| Resources | The service's containers: CPU, memory, disk I/O |
| Logs and traces | Log volume by level, slowest recent requests, failed requests (TraceQL), and the log stream |

The *Dependencies* row is where the tracing work of Parts 10–12 pays off on a dashboard. When p95 rises, it shows whether the database query or the downstream call got slower, before you open a single trace.

### Workers & Messaging

`workers()`, lines 607–671. Variables: **Worker**, **Queue** and **Log level**. Rows: queue depth, unacknowledged messages and consumers per queue; processing outcome (ack, retry, dead letter), p95 processing time and success ratio; published messages and publish failures by routing key; the chosen worker's up status, CPU, memory and business counters; cleanup sweeps by outcome and links expired; notifications by type and outcome; and the worker's logs.

**Consumers by queue** is the quickest way to spot a dead worker: a work queue with 0 consumers means nothing is reading it.

### Business

`business()`, lines 440–511. This dashboard has no variables, because it describes the whole product. It has range totals, then rows for accounts (signups and logins by outcome, login success ratio), links (created, refused by reason, deleted and expired), redirects (by outcome, hit ratio, redirect latency) and the click pipeline. The pipeline row compares clicks **published vs recorded**: when the two lines overlap, no clicks are being lost. It also shows publish failures and milestones, and the last row covers QR codes by size, rate-limit decisions, rate limiter unavailability and notifications.

Business panels also catch technical problems. A falling *login success ratio* with rising volume looks like credential stuffing. A falling *redirect hit ratio* means broken links are circulating. Rising *rate limiter unavailable* means link creation is running on the fail-open fallback.

### Infrastructure and Observability

These dashboards apply USE to each component with the metrics its exporter provides (Parts 4 and 5):

- **Docker Host:** CPU by mode, memory, disk space, throughput and busy time, load against CPU count, network throughput and errors.
- **Containers:** a sortable table of every container, then CPU, memory, disk reads and writes and out-of-memory kills, filterable by Compose project and container.
- **PostgreSQL:** connections by state and database against the maximum, longest transaction, transactions and rows per second, cache hit ratio, deadlocks, temporary files, size per database and locks by mode.
- **Redis:** clients, rejected connections, commands per second, keyspace hit ratio, memory, keys, and expired and evicted keys.
- **RabbitMQ:** queues, connections, channels and consumers, memory against its limit, free disk and alarms, message rates, problem messages (redelivered, unroutable), and depth per queue.

The *Observability* folder asks the same questions about the monitoring stack itself:

- **Prometheus:** config reload status, active series, samples appended, storage, HTTP requests by handler (including remote write), rule evaluation time and failures, and alerts sent to Alertmanager.
- **Loki:** lines and bytes received, streams in memory, lines by service and level, discarded lines by reason, request latency and the last retention run.
- **Tempo:** spans and bytes received, live traces, discarded spans, spans fed to the metrics generator, block completion failures and query latency.
- **Alloy:** running components and targets scraped, then each pipeline in turn: samples sent, retried and failed (metrics), entries sent and dropped (logs), spans accepted, refused and exported (traces).
- **Alerting:** firing and pending alerts, active silences, rule evaluation failures, and notifications by integration including failures.

## Step 6: Generate and load

Run the generator from the repository root:

```sh
python3 observability/grafana/generate_dashboards.py
```

```text
wrote dashboards/Overview/wispurl-overview.json  (23 panels)
wrote dashboards/Overview/wispurl-business.json  (25 panels)
wrote dashboards/Applications/wispurl-service.json  (27 panels)
wrote dashboards/Applications/wispurl-workers.json  (23 panels)
wrote dashboards/Infrastructure/wispurl-host.json  (14 panels)
...
wrote dashboards/Observability/wispurl-alerting.json  (9 panels)
```

The first time, restart Grafana so it reads the changed provider file:

```sh
docker compose -f compose.observability.yaml restart grafana
```

After that, a regenerated file goes live within 30 seconds. Commit the script and the generated JSON together, so the two never disagree.

## How to change a dashboard

1. Edit the dashboard's function in `generate_dashboards.py`: add a panel to a `L.add([...])` call, change a query or a threshold.
2. Run the generator and look at the diff of the JSON. A small script change should give a small, readable JSON change.
3. Wait up to 30 seconds and check the dashboard in Grafana.
4. Commit both files.

To try out a panel interactively first, use Grafana's **Explore**, or save a copy of the dashboard to a scratch folder with **Save as** and experiment there. When the query is right, copy it into the script and delete the scratch copy.

## Check that it works

Open http://127.0.0.1:3001 → **Dashboards**. You should see the four folders, and **Overview → WispURL — System Overview** should be mostly green.

**Generate realistic traffic.** Request metrics only need redirects, but business panels need every path: sign up (twice with the same email, for a `duplicate_email`), log in with a wrong password, create links with and without a custom slug, follow them, request unknown short codes, generate QR codes in several sizes, and delete a link. Creating more than `CREATE_LINK_LIMIT` links in an hour also fills the *refused: rate_limited* line.

Then check the numbers agree with each other. On the test run for this article, 60 redirects gave:

| Panel | Value |
| --- | --- |
| Business → Redirects served | 60 |
| Workers → Published (`link.clicked`) | 60 |
| Workers → Processed (`analytics.clicks`, ack) | 60 |
| Business → Clicks recorded | 60 |

When those four agree, the click pipeline is measured correctly from end to end.

**Follow a drill-down.** On the Overview, click `shortener-service` in the *Service health* table. Service Detail opens with the service selected and the same time range. Change **Route** to `/{short_code}` and every panel narrows to redirects. Open a trace from *Slowest recent requests*.

**Exercise the event-driven panels.** Some panels only fill when something happens. To see them, create a link that expires in a minute. Within one cleanup sweep, *Links expired* and *Notifications (link_expired, sent)* each go to 1. Follow one link 100 times and *Milestones reached* shows a bar for the 100 threshold, with a matching milestone notification.

**Check every query automatically.** It's worth having a small script that reads each generated JSON file, replaces the variables with real values, and runs every Prometheus, Loki and Tempo query against the APIs, reporting errors and empty results. On a healthy stack with some traffic, expect **no errors**. A few panels stay empty, and that is correct: they count events that haven't happened, such as 5xx responses, publish failures, dead letters, failed notifications, firing alerts, slow or failed traces and dropped log lines. An empty *host CPU* panel, on the other hand, is a bug.

**Confirm the protection.** Try to save a change to any provisioned dashboard. Grafana refuses, because it was provisioned.

## When something goes wrong

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Folders are lowercase or named after old directories | Grafana reuses a folder it created earlier, even after the directory is renamed | Rename the folder in the UI, or delete the empty old folder; new folders take the directory's exact name |
| Dashboards don't appear | Provider file not reloaded, or a `folder:` value left next to `foldersFromFilesStructure` | Remove `folder:`, then restart Grafana once |
| Worker panels are empty | Workers not rebuilt, or missing scrape labels | `docker compose up -d --build <worker>`; check that the worker appears in Alloy's UI as a scrape target |
| A worker crashes with `ModuleNotFoundError: starlette` | The package `__init__` imports the HTTP middleware eagerly | Use the lazy `__getattr__` from Step 1 |
| Business panel says "No data" | That event hasn't happened in the selected range | Widen the time range or trigger the event; stats use `or vector(0)` to show 0 instead |
| Per-container network panels are empty | cAdvisor on Docker Desktop can't see per-container network traffic | Expected on macOS and Windows; the dashboards show disk I/O instead. On a Linux host, `container_network_*` metrics are available |
| *Dependencies* row is empty | Tempo span metrics or service graph not enabled, or no recent traffic | Check the `metrics_generator` processors from Part 9; generate traffic |
| A data link opens the dashboard with "All" selected | The variable name in `link_to()` doesn't match the target dashboard's variable | Use the exact variable name (`service`, `worker`, `queue`) |
| A change to the script doesn't show up | The generator wasn't run, or Grafana hasn't reloaded yet | Run the generator; wait 30 seconds; check `docker compose -f compose.observability.yaml logs grafana` |

## What you have now

- A **System Overview** that answers "is anything broken?" in one screen, with every number linking to the details.
- **Service Detail** and **Workers & Messaging** pages, where you pick a service, worker or queue and see its RED signals, dependencies, resources, logs and traces together.
- A **Business** dashboard backed by low-cardinality product metrics, including an end-to-end check of the click pipeline.
- **Infrastructure** and **Observability** folders covering the dependencies and the monitoring stack itself.
- Worker metrics endpoints, and worker healthchecks that check something real.
- Everything generated from one script, provisioned from Git, and protected from accidental edits.

Dashboards help when someone is looking. In [Part 15](15-alerting-with-alertmanager.md) we make the system tell you when something is wrong, with alert rules, routing and local email delivery.

## Key takeaways

- Organise dashboards as a hierarchy: an overview with thresholds, then drill-down pages with variables, then traces and logs.
- One dashboard per kind of thing, with a drop-down, beats one dashboard per instance. It only works when labels are consistent across metrics, logs and traces.
- Split folders by audience: overview, applications, infrastructure, and the monitoring stack itself.
- Measure business events, and keep their labels to small fixed sets. Never use IDs, emails or URLs as labels.
- Background workers need a metrics endpoint and queue metrics; HTTP metrics never see them.
- Generate dashboards from code once they share panels and conventions; commit both the generator and its output.
- Make "nothing happened" show as 0, not "No data", so an empty panel always means something is wrong.

## FAQ

### How do I organise Grafana dashboards for a microservices system?

Start with one overview dashboard that shows overall health, service status, key business numbers and infrastructure, each with a colour threshold. Link every number to a detail dashboard that uses a template variable to select one service, worker or queue. Group dashboards into folders by audience, such as Overview, Applications, Infrastructure and Observability.

### How do I put provisioned Grafana dashboards in folders?

Set `foldersFromFilesStructure: true` in the file provider and put each dashboard JSON file in a subdirectory of the provider's path. Grafana creates one folder per subdirectory, using the directory name as the folder name. Remove any `folder:` setting, because the two can't be combined.

### How do I generate Grafana dashboards with Python?

Write small functions that return panel dictionaries (time series, stat, table, logs), a layout helper that assigns grid positions on Grafana's 24-column grid, and a wrapper that adds the uid, title, tags, variables and links. Then write each dashboard with `json.dumps`. Commit the generated JSON so Grafana loads it through file provisioning. The Grafana Foundation SDK offers typed builders if you prefer a library.

### How do I link from one Grafana dashboard to another with the same filter?

Add a data link with the URL `/d/<uid>?${__url_time_range}&var-<variable>=${__value.raw}`. `${__url_time_range}` keeps the time range, and `var-<variable>` sets the target dashboard's variable to the clicked value.

### What business metrics should a web application export to Prometheus?

Count the product's key events by outcome: sign-ups, logins, the main action (here, links created and redirects served), background work completed, and notifications sent. Add ratios on the dashboard, such as login success or redirect hit ratio. Keep every label to a small fixed set of values, and send per-user or per-item analysis to a database, not to Prometheus.

### How do I expose Prometheus metrics from a Python worker without a web framework?

Call `prometheus_client.start_http_server(port)` when the worker starts. It serves `/metrics` from a background thread. Don't use it in multi-process servers such as Gunicorn, where each process has its own metrics; use the client's multiprocess mode there instead.

### Why does my Grafana panel show "No data" instead of 0?

Prometheus has no series for a counter label combination that has never been used, so a query for it returns nothing. Add `or vector(0)` to single-value queries, or, for ratios, fall back to `<denominator> * 0`, so the panel shows a real zero.

---

**Series navigation:** Previous: [Part 13, Link Logs and Traces](13-link-logs-and-traces.md) · [Series index](README.md) · Next: [Part 15, Alerting with Prometheus and Alertmanager](15-alerting-with-alertmanager.md)
