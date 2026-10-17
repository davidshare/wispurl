---
title: "Observability for WispURL, Part 9: Store Traces in Tempo"
seo_title: "Grafana Tempo 3 with Docker Compose and Alloy OTLP"
slug: grafana-tempo-3-docker-compose-alloy-otlp
description: "Run Grafana Tempo 3.1 with Docker Compose, receive OpenTelemetry traces through Alloy, set retention and limits, and generate span metrics."
series: "Observability for WispURL"
part: 9
date: 2026-10-17
last_updated: 2026-10-17
author: David Essien
tags: [tempo, tracing, opentelemetry, otlp, grafana-alloy, docker-compose]
keywords:
  - "Grafana Tempo Docker Compose"
  - "Tempo 3 configuration"
  - "Tempo metrics generator service graph"
  - "OTLP Grafana Alloy Tempo"
  - "Tempo retention block_retention"
  - "span metrics Prometheus"
  - "distributed tracing backend"
difficulty: intermediate
estimated_time: 35 minutes
prerequisites:
  - "Part 8: Ship Container Logs with Alloy"
repo_files:
  - observability/tempo/tempo.yaml
  - compose.observability.yaml
  - observability/alloy/config.alloy
  - observability/prometheus/prometheus.yml
  - observability/grafana/provisioning/datasources/datasources.yaml
---

# Observability for WispURL, Part 9: Store Traces in Tempo

> **In short:** run Tempo `3.1.0` as a single binary (`-target=all`) with local storage, and keep it off the host's network: services send OpenTelemetry spans to Grafana Alloy on port 4317, Alloy batches them and forwards them to Tempo. Set retention per tenant with `overrides.defaults.compaction.block_retention`, cap ingestion and trace size, and turn on the metrics generator's `service-graphs` and `span-metrics` processors so Tempo writes request rates, errors, latency and a service map into Prometheus.

Metrics say *something* is slow; logs say *what* happened. **Traces** say *where*: they record one request's journey through every service it touches, with timings for each step. In this part you'll deploy **Tempo**, the trace store, and route traces to it through Alloy. The services start producing traces in Part 10.

## Traces in two minutes

A **trace** is the full story of one request. It's made of **spans**: one span per unit of work, each with a start time, a duration, a name and attributes.

```text
Trace 39d307d3…  (one redirect, 48 ms)
└─ gateway        GET /{short_code}                       48 ms
   └─ gateway     GET  (call to shortener)                 41 ms
      └─ shortener GET /{short_code}                      38 ms
         ├─ shortener SELECT short_db                       4 ms
         └─ shortener link.clicked publish                 2 ms
            └─ analytics-consumer analytics.clicks process 12 ms
               └─ analytics-consumer INSERT stats_db         3 ms
```

*Figure: one WispURL redirect as a trace. Each line is a span; nesting shows which work caused which.*

Every span carries the **trace ID** it belongs to and its parent's **span ID**. That's how a backend reassembles the tree, even though each service sent its spans separately. How those IDs get passed between services is Part 11.

**OTLP** (OpenTelemetry Protocol) is the standard wire format for sending spans, on port **4317** (gRPC) or **4318** (HTTP).

## Design decisions

### Why Tempo?

Part 0 compared Tempo with Jaeger. To recap the deciding points: Tempo stores traces as plain files (or objects in S3), with no database to run; it's indexed by trace ID plus a compact set of attributes, which keeps it cheap; and it can turn traces into metrics and link to Loki and Prometheus inside Grafana.

### Services send to Alloy, not straight to Tempo

Tempo can receive OTLP itself, so why go through Alloy?

- **One destination for every service.** Services are configured with `alloy:4317` once. If the backend changes (another Tempo, a managed tracing service, a second backend for comparison), only Alloy's config changes.
- **Batching.** Alloy groups spans from many requests into larger batches, which is far more efficient for Tempo than thousands of tiny writes.
- **Buffering and retries.** If Tempo restarts, Alloy holds and retries rather than every service dropping spans.
- **A place to process traces.** Sampling, attribute redaction or enrichment can be added in one place later, without touching services.

So Tempo **doesn't publish its OTLP ports** to the host at all. Only its query API (3200) is published, for Grafana and for testing. Alloy publishes OTLP on `127.0.0.1` instead, for services you run directly on your machine during development.

### Tempo 3 changed its internals

If you've used Tempo 2, you'll notice that `ingester` and `compactor` blocks are gone. Tempo 3 reorganised how it works internally: recent traces are held by a **live store**, blocks are written by a **block builder**, and compaction and retention run as jobs on a **backend scheduler** and **backend workers**. In single-binary mode (`-target=all`) all of these run inside one process with sensible defaults, so you don't configure them individually. Two practical consequences:

- **Copy-pasted Tempo 2 configs fail to start** with errors like `field compactor not found in type app.Config`.
- **Retention is set through `overrides`** (per tenant), not a `compactor` block.

### Retention and size

Traces are the most expensive signal per request: one request can produce dozens of spans, each with attributes. WispURL keeps traces for **31 days** to match logs, so a trace ID found in an old log line still opens. On the stack in this series, that has used about 60 MB so far.

In production, traces are usually kept for days, not weeks, and **sampled** (only a percentage of requests recorded). We record every request locally (Part 10 explains the sampling setting), because the volume is tiny and seeing every request is how you learn.

### Generate metrics from traces

Tempo's **metrics generator** reads spans as they arrive and writes Prometheus metrics:

| Processor | Produces | Gives you |
| --- | --- | --- |
| `span-metrics` | `traces_spanmetrics_calls_total`, `traces_spanmetrics_latency_bucket` | Request rate, errors and latency per service and span name, derived from traces |
| `service-graphs` | `traces_service_graph_request_total`, `..._failed_total`, `..._seconds_bucket` | Which service calls which, how often, how many fail, how fast. Grafana draws it as a map. |

Part 2's RED metrics come from inside each service. Span metrics come from the traces, so they also cover hops a service doesn't measure itself, such as calls to RabbitMQ and the database. The service graph in particular is hard to get any other way.

## Step 1: Write the Tempo config

Create `observability/tempo/tempo.yaml`:

```yaml
server:
  http_listen_port: 3200
  grpc_listen_port: 9095
  log_level: info

distributor:
  receivers:
    otlp:
      protocols:
        grpc:
          endpoint: 0.0.0.0:4317
        http:
          endpoint: 0.0.0.0:4318

storage:
  trace:
    backend: local
    wal:
      path: /var/tempo/wal
    local:
      path: /var/tempo/blocks

metrics_generator:
  registry:
    external_labels:
      source: tempo
      cluster: docker-compose
  storage:
    path: /var/tempo/generator/wal
    remote_write:
      - url: http://prometheus:9090/api/v1/write

overrides:
  defaults:
    # The generator does nothing until processors are enabled. These two derive
    # a service graph and request/error/duration metrics from spans.
    metrics_generator:
      processors: [service-graphs, span-metrics]
    compaction:
      block_retention: 744h
    ingestion:
      rate_limit_bytes: 15000000
      burst_size_bytes: 20000000
    global:
      max_bytes_per_trace: 5000000

usage_report:
  reporting_enabled: false
```

> `observability/tempo/tempo.yaml` lines 1–48.

Section by section:

- **`server`**: port 3200 is the HTTP API (queries, `/ready`, `/metrics`); 9095 is internal gRPC.
- **`distributor.receivers.otlp`**: accept OTLP over gRPC (4317) and HTTP (4318). Only Alloy will send here, over the private `observability` network. Tempo also understands Jaeger and Zipkin formats; enable only the receivers you use, because every open port is something else to secure.
- **`storage.trace`**: `backend: local` stores blocks on disk under `/var/tempo/blocks`. The **WAL** (write-ahead log) records incoming spans immediately, so a crash doesn't lose recent traces. In the cloud you'd set `backend: s3` with a bucket.
- **`metrics_generator`**:
  - `registry.external_labels` adds `source="tempo"` (and `cluster`) to every generated series, so you can tell trace-derived metrics apart;
  - `storage.path` is the generator's own WAL;
  - `remote_write` pushes the metrics to Prometheus, using the receiver enabled in Part 1.
- **`overrides.defaults`**: per-tenant settings, applied to every tenant (with auth off there's one tenant, `single-tenant`):
  - **`metrics_generator.processors`**: the switch. Configuring `metrics_generator` alone produces **nothing** until processors are listed here. This is the Tempo equivalent of Loki's retention trap.
  - **`compaction.block_retention: 744h`**: keep 31 days of traces. Tempo's built-in default is 14 days.
  - **`ingestion.rate_limit_bytes` / `burst_size_bytes`**: about 15 MB/s sustained and 20 MB/s burst. Like Loki's limits, these exist to protect Tempo from a runaway client, not to constrain normal traffic.
  - **`global.max_bytes_per_trace: 5000000`**: a single trace larger than 5 MB is cut off. Huge traces usually come from a bug, such as a loop creating spans, and can make queries slow or crash the UI.
- **`usage_report.reporting_enabled: false`**: no anonymous usage reporting.

## Step 2: Add Tempo to Compose

```yaml
  tempo:
    image: ${TEMPO_IMAGE:-grafana/tempo:3.1.0}
    restart: unless-stopped
    command:
      - -config.file=/etc/tempo/tempo.yaml
      - -target=all
    ports:
      - "127.0.0.1:${TEMPO_HTTP_PORT:-3200}:3200"
    volumes:
      - ./observability/tempo/tempo.yaml:/etc/tempo/tempo.yaml:ro
      - tempo-data:/var/tempo
    networks:
      - observability
    healthcheck:
      # The Tempo image has no shell; its binary can check its own /ready endpoint.
      test: ["CMD", "/tempo", "-health"]
      interval: 15s
      timeout: 5s
      retries: 10
      start_period: 30s
    logging: *default-logging
```

> `compose.observability.yaml` lines 58–78.

Add `tempo-data:` to `volumes:`. Then make Alloy and Grafana wait for Tempo, in their `depends_on` blocks:

```yaml
      tempo:
        condition: service_healthy
```

> `compose.observability.yaml` lines 120–121 (Alloy) and 163–164 (Grafana).

- **`-target=all`** runs every Tempo component in one process: single-binary mode.
- **Only port 3200 is published.** No 4317/4318 on the host; spans come from Alloy over the private network.
- **Healthcheck.** The Tempo image contains only the Tempo binary: no shell, no `wget`. Like Loki, it has a built-in `-health` flag that checks `/ready`. This is the third healthcheck technique in this series: `wget` where it exists (Prometheus, Grafana), bash `/dev/tcp` where there's a shell but no HTTP client (Alloy), and a built-in flag where there's nothing at all (Loki, Tempo).

## Step 3: Route traces through Alloy

Append to `config.alloy`:

```alloy
otelcol.receiver.otlp "default" {
  grpc {
    endpoint = "0.0.0.0:4317"
  }

  http {
    endpoint = "0.0.0.0:4318"
  }

  output {
    traces = [otelcol.processor.batch.default.input]
  }
}

// Group spans into batches before sending: fewer, larger requests to Tempo.
otelcol.processor.batch "default" {
  timeout = "5s"

  output {
    traces = [otelcol.exporter.otlp.tempo.input]
  }
}

otelcol.exporter.otlp "tempo" {
  client {
    endpoint = "tempo:4317"

    tls {
      insecure = true
    }
  }
}
```

> `config.alloy` lines 292–323.

These `otelcol.*` components are OpenTelemetry Collector components embedded in Alloy, so the vocabulary matches the wider OpenTelemetry world: **receiver → processor → exporter**.

- **`otelcol.receiver.otlp`** listens on 4317 and 4318 on all Alloy's networks, including the WispURL network where the services are. `output.traces` passes spans on.
- **`otelcol.processor.batch`** collects spans and sends them in batches: when the batch is full (8,192 spans by default) or 5 seconds have passed, whichever comes first. A 5-second wait is invisible for traces, which are looked at after the fact.
- **`otelcol.exporter.otlp`** sends batches to Tempo over gRPC. `tls.insecure = true` because the traffic stays on a private Docker network; across real networks you'd use TLS.

Publish Alloy's OTLP ports on localhost, in the `alloy` service's `ports`:

```yaml
      # OTLP for services run directly on the host (containers use alloy:4317).
      - "127.0.0.1:${OTLP_GRPC_PORT:-4317}:4317"
      - "127.0.0.1:${OTLP_HTTP_PORT:-4318}:4318"
```

> `compose.observability.yaml` lines 93–95.

Containers reach Alloy at `alloy:4317` on the WispURL network. These host ports are only for running a service outside Docker, with `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317`.

## Step 4: Monitor Tempo and connect Grafana

Prometheus scrapes Tempo, in `prometheus.yml`:

```yaml
  - job_name: tempo
    static_configs:
      - targets:
          - tempo:3200
        labels:
          environment: docker
          application: observability
```

> `prometheus.yml` lines 45–51.

Add Tempo to Grafana's data sources, after Loki:

```yaml
  - name: Tempo
    uid: tempo
    type: tempo
    access: proxy
    url: http://tempo:3200
    jsonData:
      # Service map built from Tempo's metrics-generator series in Prometheus.
      serviceMap:
        datasourceUid: prometheus
      nodeGraph:
        enabled: true
```

> `datasources.yaml` lines 31–35 and 46–50. Part 13 adds a `tracesToLogsV2` block between them.

- **`serviceMap.datasourceUid: prometheus`** tells Grafana to build the service map from the `traces_service_graph_*` metrics in Prometheus. That's why the UIDs from Part 6 are fixed.
- **`nodeGraph.enabled`** shows each trace as a small graph of services as well as a timeline.

Start everything:

```sh
docker compose -f compose.observability.yaml up -d
curl -X POST http://127.0.0.1:9090/-/reload
docker compose -f compose.observability.yaml restart alloy grafana
```

## Check that it works

The services don't create traces until Part 10, so send Tempo a hand-made trace: two spans, a client in `test-client` calling a server in `test-server`, posted as OTLP JSON to Alloy's HTTP port. The whole path is tested: Alloy, batching, Tempo, the metrics generator and Prometheus.

```sh
python3 - <<'EOF'
import json, os, time, urllib.request
now = time.time_ns(); tid = os.urandom(16).hex(); client = os.urandom(8).hex(); server = os.urandom(8).hex()
def rs(svc, span):
    return {"resource": {"attributes": [{"key": "service.name", "value": {"stringValue": svc}}]},
            "scopeSpans": [{"spans": [span]}]}
body = {"resourceSpans": [
  rs("test-client", {"traceId": tid, "spanId": client, "name": "GET /test", "kind": 3,
                     "startTimeUnixNano": str(now), "endTimeUnixNano": str(now + 50_000_000)}),
  rs("test-server", {"traceId": tid, "spanId": server, "parentSpanId": client, "name": "GET /test", "kind": 2,
                     "startTimeUnixNano": str(now + 5_000_000), "endTimeUnixNano": str(now + 45_000_000)}),
]}
req = urllib.request.Request("http://127.0.0.1:4318/v1/traces", json.dumps(body).encode(),
                             {"Content-Type": "application/json"})
print("status", urllib.request.urlopen(req).status, "trace id", tid)
EOF
```

`kind: 3` is a CLIENT span and `kind: 2` is a SERVER span; the server span's `parentSpanId` is the client span. That parent-child link across two services is exactly what the service graph is built from.

**1. Fetch the trace from Tempo** (wait about 10 seconds for the batch to flush):

```sh
curl -s http://127.0.0.1:3200/api/v2/traces/<trace id> | python3 -m json.tool | head -30
```

**2. See it in Grafana.** Explore → **Tempo** → query type **TraceQL**, then:

```traceql
{ resource.service.name = "test-server" }
```

Click the result: a timeline with the client span and the server span nested inside it.

**3. Check the generated metrics.** After about a minute, in Prometheus:

```promql
sum by (service) (traces_spanmetrics_calls_total{service=~"test-.*"})
```

returns one call each for `test-client` and `test-server`, and

```promql
traces_service_graph_request_total{client="test-client"}
```

returns one edge: `client="test-client"`, `server="test-server"`. Tempo turned two spans into a service map.

**4. Prometheus sees Tempo:** `up{job="tempo"}` is `1`.

## When something goes wrong

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Tempo won't start: `field compactor not found in type app.Config` | A Tempo 2 config on Tempo 3 | Remove the `compactor` block; set retention under `overrides.defaults.compaction`. |
| `field traces_storage not found` | Another Tempo 2 setting | Remove `metrics_generator.traces_storage`. |
| No `traces_spanmetrics_*` or `traces_service_graph_*` metrics | Processors not enabled, or remote write rejected | List them under `overrides.defaults.metrics_generator.processors`; make sure Prometheus has `--web.enable-remote-write-receiver`. |
| Service graph has no edges | Only one service's spans arrived, or no CLIENT/SERVER pair | Edges need a CLIENT span in one service and a SERVER child in another. Part 11 makes the services produce these. |
| `connection refused` posting to `127.0.0.1:4318` | Alloy's OTLP ports not published | Add the two port lines to the `alloy` service. |
| Trace found by ID but not by search | Search indexes recent data shortly after ingestion | Wait a few seconds and search again. |

## What you have now

- Tempo `3.1.0` storing traces for 31 days, with ingestion and trace-size limits.
- Alloy receiving OTLP from services, batching it and forwarding to Tempo.
- Span metrics and a service graph flowing into Prometheus.
- Tempo connected to Grafana, with the service map enabled.

All three stores are ready. Next, the services need to produce traces. In [Part 10](10-instrument-services-with-opentelemetry.md) we add OpenTelemetry to every service through one shared library.

## Key takeaways

- A trace is a tree of spans linked by trace and span IDs; OTLP on 4317/4318 is how spans travel.
- Send spans to a collector, not straight to the backend: one destination, batching, retries, and a single place to process traces.
- Don't publish Tempo's receiver ports to the host when a collector sits in front.
- Tempo 3 dropped the `compactor` and `ingester` blocks. Set retention with `overrides.defaults.compaction.block_retention`.
- The metrics generator does nothing until processors are listed under `overrides`.
- Span metrics and the service graph give you RED metrics and a service map derived from traces, including hops services don't measure themselves.

## FAQ

### How do I run Grafana Tempo with Docker Compose?

Use a pinned image such as `grafana/tempo:3.1.0` with `-target=all`, mount a config with an OTLP receiver and `storage.trace.backend: local`, store data in a named volume at `/var/tempo`, and publish port 3200 for queries. Use `/tempo -health` as the healthcheck, because the image has no shell.

### How do I set trace retention in Tempo 3?

Set `overrides.defaults.compaction.block_retention` (for example `744h` for 31 days). Tempo 3 removed the `compactor` configuration block, so Tempo 2 examples that set retention there fail to start.

### Why is the Tempo metrics generator not producing metrics?

The generator only runs processors listed in `overrides.defaults.metrics_generator.processors`, such as `[service-graphs, span-metrics]`. Also check that `metrics_generator.storage.remote_write` points at a Prometheus started with `--web.enable-remote-write-receiver`.

### Should applications send traces directly to Tempo?

They can, but sending to a collector (Grafana Alloy or the OpenTelemetry Collector) is usually better. Services then have one fixed destination, spans are batched and retried, and sampling or redaction can be added in one place.

### What is a service graph in Tempo?

A map of which services call which, built by Tempo's `service-graphs` processor from pairs of CLIENT and SERVER spans. It produces `traces_service_graph_request_total` and related metrics in Prometheus, which Grafana renders as a node graph with request rates, error rates and latencies on each edge.

---

**Series navigation:** Previous: [Part 8, Ship Container Logs with Alloy](08-ship-container-logs-with-alloy.md) · [Series index](README.md) · Next: [Part 10, Instrument Services with OpenTelemetry](10-instrument-services-with-opentelemetry.md)
