---
title: "Observability for WispURL, Part 7: Store Logs in Loki"
seo_title: "Run Grafana Loki with Docker Compose and Real Retention"
slug: grafana-loki-docker-compose-retention
description: "Run Grafana Loki 3 in single-binary mode with Docker Compose, choose a schema and limits, and enforce log retention with the compactor so disks never fill."
series: "Observability for WispURL"
part: 7
date: 2026-10-17
last_updated: 2026-10-17
author: David Essien
tags: [loki, logging, docker-compose, retention, grafana]
keywords:
  - "Grafana Loki Docker Compose"
  - "Loki retention not working"
  - "Loki compactor retention_enabled"
  - "Loki schema v13 tsdb"
  - "Loki structured metadata"
  - "Loki push API curl"
  - "Loki labels cardinality"
difficulty: intermediate
estimated_time: 30 minutes
prerequisites:
  - "Part 6: Deploy Grafana"
repo_files:
  - compose.observability.yaml
  - observability/loki/loki.yaml
  - observability/prometheus/prometheus.yml
---

# Observability for WispURL, Part 7: Store Logs in Loki

> **In short:** run Loki `3.7.8` as a single binary with filesystem storage and the `tsdb` index (schema `v13`). Set `retention_period` **and** enable the compactor with `retention_enabled: true`; without the compactor, Loki never deletes anything. Reject old samples, allow structured metadata (needed later for trace IDs), and keep labels to a small set of low-cardinality values. Test it by pushing a line with `curl` and reading it back.

Metrics told us *that* something is wrong; logs tell us *why*. In this part you'll deploy **Loki**, the log store. Nothing ships logs to it yet (that's Part 8), so you'll test it by pushing a log line by hand.

## How Loki stores logs

Understanding Loki's data model explains every config decision that follows.

Loki groups log lines into **streams**. A stream is every line that shares the same set of **labels**:

```text
{service="shortener-service", level="error"}   ← one stream
{service="shortener-service", level="info"}    ← another stream
{service="auth-service", level="info"}         ← another stream
```

Loki builds an **index of labels only**. The text of each line is compressed into **chunks** and never indexed word by word. A query works in two steps:

1. use the index to find the streams whose labels match, such as `{service="shortener-service", level="error"}`;
2. decompress those streams' chunks and scan the text, such as `|= "timeout"`.

This is why Loki is cheap: the index is tiny. It's also why **labels must have few values**. Every unique label combination is a new stream with its own chunks. A label like `request_id` would create a new stream for every request: millions of tiny chunks, a huge index, and slow queries. The rules from Part 2 apply here too:

| Good labels (few values) | Bad labels (unbounded) |
| --- | --- |
| `service`, `container`, `level`, `environment` | `request_id`, `trace_id`, `user_id`, `short_code`, IP addresses |

So where do request IDs and trace IDs go? Into **structured metadata**: key-value pairs attached to individual lines, stored with the chunk, searchable, but **not** part of the index. We'll use that in Part 8.

## Design decisions

### Single binary, filesystem storage

Loki can run as one process or as a dozen separate microservices (distributors, ingesters, queriers, compactors…) for clusters that ingest terabytes a day. On one machine, the single-binary mode runs all of those inside one process. It's the only sensible choice locally.

For storage, Loki can use object storage (S3, GCS, Azure) or the local filesystem. Object storage is what you'd use in the cloud: durable, cheap, and shared by every Loki instance. Locally, the filesystem in a Docker volume is enough.

### The schema: `tsdb` and `v13`

The `schema_config` decides how the index is built. **Schemas are versioned and permanent for the data they wrote**: you can't edit an existing entry, only add a new one that starts on a later date. Choose the current recommendation from day one: the `tsdb` index store with schema `v13`, the only combination that supports structured metadata. Older guides that use `boltdb-shipper` or `v11` describe deprecated setups.

### Retention needs the compactor

This is the trap in Loki configuration. `limits_config.retention_period` only **declares** how long to keep data. The component that actually deletes expired chunks is the **compactor**, and it only does so when `retention_enabled: true` is set. Configure `retention_period` alone and nothing is ever deleted: the volume grows until the disk is full.

### How long to keep logs

WispURL keeps logs for **31 days** (`744h`), longer than Prometheus's 15 days. The reasoning: logs are what you reach for when investigating something reported late ("a user says links broke last Tuesday"), or when reviewing security events. At local volumes the cost is negligible. On the stack in this series, Loki receives under 100 bytes per second on average and its volume holds well under a megabyte.

To size retention for a real system, use the same approach as Prometheus:

```text
disk ≈ bytes ingested per day × retention days ÷ compression ratio (typically 5–10×)
```

You can measure ingestion with `sum(rate(loki_distributor_bytes_received_total[1h]))` once Prometheus scrapes Loki (Step 3). In production, log volume, not metrics, is usually what drives storage costs, and 7 to 14 days of "hot" logs is common, with older logs archived elsewhere.

### Reject old samples

If a collector replays an old log file, or a container's clock is wrong, Loki would accept lines with timestamps weeks in the past. Those lines land in time ranges the compactor may already have cleaned up, and they confuse queries. `reject_old_samples` refuses lines older than `reject_old_samples_max_age` (7 days here).

### Single tenant

Loki supports **multi-tenancy**: every request carries an `X-Scope-OrgID` header and each tenant's data is kept separate. `auth_enabled: false` turns this off: all data belongs to one built-in tenant and no header is required. That's right for one team's local stack. A shared Loki in production would turn it on and put an authenticating proxy in front.

## Step 1: Write the Loki config

Create `observability/loki/loki.yaml`. Here it is in sections.

### Server and common settings

```yaml
auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  instance_addr: 0.0.0.0
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory
```

> `loki.yaml` lines 1–17.

- **Port 3100** is Loki's HTTP API: pushing, querying, health and metrics. 9096 is gRPC, used between Loki's own components.
- **`common`** sets defaults that every internal component inherits, so you don't repeat storage paths for each one.
- **`/loki`** is the named volume (Step 2). Chunks, the index and the compactor's working files all live under it.
- **`replication_factor: 1`** and **`ring.kvstore: inmemory`**: in a cluster, Loki keeps several copies of recent data and coordinates its components through a shared key-value store (the "ring"). With one process there's nothing to replicate or coordinate, so it keeps that state in memory.

### Schema

```yaml
schema_config:
  configs:
    - from: 2024-01-01
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h
```

> `loki.yaml` lines 19–27.

- **`from`** is the date this schema applies from. Choose a date in the past for a new install. To change schema later, add a second entry with a future `from` date and leave this one alone.
- **`period: 24h`** creates one index table per day. Retention deletes whole days of index, and 24h is the only period the `tsdb` store supports.

### Limits

```yaml
limits_config:
  # Enforced by the compactor below; without it nothing is ever deleted.
  retention_period: 744h
  # Refuse entries older than 7 days (e.g. a replayed old log file).
  reject_old_samples: true
  reject_old_samples_max_age: 168h
  allow_structured_metadata: true
  ingestion_rate_mb: 16
  ingestion_burst_size_mb: 24
```

> `loki.yaml` lines 29–37.

- **`retention_period: 744h`**: 31 days. Loki uses hours; `31d` isn't accepted here.
- **`allow_structured_metadata: true`**: lets Alloy attach `request_id`, `trace_id` and `span_id` to each line without making them labels.
- **`ingestion_rate_mb` / `ingestion_burst_size_mb`**: per-tenant rate limits, in megabytes per second. If a container gets stuck in a loop printing errors, Loki rejects the excess instead of being overwhelmed. Alloy retries rejected pushes, so short bursts aren't lost. 16 MB/s is far above anything WispURL produces, so this only ever triggers on a runaway.

### Compactor: where retention actually happens

```yaml
# The compactor applies retention_period: it marks expired chunks and deletes
# them retention_delete_delay later.
compactor:
  working_directory: /loki/compactor
  compaction_interval: 10m
  retention_enabled: true
  retention_delete_delay: 2h
  delete_request_store: filesystem
```

> `loki.yaml` lines 39–46.

- **`compaction_interval: 10m`**: how often the compactor runs. Each run merges small index files and marks chunks older than the retention period.
- **`retention_enabled: true`**: the switch that makes retention happen.
- **`retention_delete_delay: 2h`**: marked chunks are deleted two hours later, which gives running queries time to finish with them.
- **`delete_request_store: filesystem`**: where the compactor records pending deletions. It's required whenever retention is enabled, and Loki refuses to start without it.

### Ruler and analytics

```yaml
# Minimal ruler config for local dev (optional but safe)
ruler:
  storage:
    type: local
    local:
      directory: /loki/rules
  rule_path: /loki/rules-temp
  ring:
    kvstore:
      store: inmemory
  enable_api: true

analytics:
  reporting_enabled: false
```

> `loki.yaml` lines 48–63.

- The **ruler** evaluates alert rules written in LogQL, such as "more than 10 `panic` lines a minute". We alert from Prometheus in this series, so it has no rules yet. The block is here so you can add log-based alerts later without restructuring the file.
- **`analytics.reporting_enabled: false`** turns off anonymous usage reporting. As a side benefit, it avoids a known start-up error where Loki tries to write a cluster-ID file it lacks permission for.

### Validate

Loki can check a config without starting:

```sh
docker run --rm -v "$PWD/observability/loki:/c:ro" grafana/loki:3.7.8 \
  -config.file=/c/loki.yaml -verify-config
```

```text
level=info ... msg="config is valid"
```

## Step 2: Add Loki to Compose

Add to `compose.observability.yaml`:

```yaml
  loki:
    image: ${LOKI_IMAGE:-grafana/loki:3.7.8}
    restart: unless-stopped
    command:
      - -config.file=/etc/loki/loki.yaml
    ports:
      - "127.0.0.1:${LOKI_PORT:-3100}:3100"
    volumes:
      - ./observability/loki/loki.yaml:/etc/loki/loki.yaml:ro
      - loki-data:/loki
    networks:
      - observability
    healthcheck:
      test: ["CMD", "/usr/bin/loki", "-health"]
      interval: 10s
      timeout: 5s
      retries: 12
      start_period: 60s
    logging: *default-logging
```

> `compose.observability.yaml` lines 38–56.

Add `loki-data:` to the `volumes:` list. In the `grafana` service, add Loki to `depends_on`, so Grafana waits for it:

```yaml
      loki:
        condition: service_healthy
```

> `compose.observability.yaml` lines 161–162.

- **Healthcheck.** The Loki image has no shell tools, but the Loki binary has a `-health` flag that checks its own `/ready` endpoint and exits 0 or 1. Use a binary's built-in health flag when an image is too minimal for anything else.
- **`start_period: 60s`** gives Loki a minute after starting before failed checks count, because it replays its write-ahead log on start-up, which can take a while after a crash.
- **Port 3100 on localhost** is published only so you can test it with `curl`. Day to day, you'll query Loki through Grafana.

## Step 3: Let Prometheus monitor Loki

Add to `prometheus.yml`:

```yaml
  - job_name: loki
    static_configs:
      - targets:
          - loki:3100
        labels:
          environment: docker
          application: observability
```

> `prometheus.yml` lines 37–43.

Start Loki and reload Prometheus:

```sh
docker compose -f compose.observability.yaml up -d
curl -X POST http://127.0.0.1:9090/-/reload
```

## Check that it works

**1. Loki is ready:**

```sh
curl http://127.0.0.1:3100/ready
```

```text
ready
```

(For the first few seconds after starting it may say `Ingester not ready: waiting for 15s after being ready`. Wait and retry.)

**2. Push a log line by hand.** Loki's push API takes JSON: a list of streams, each with labels and `[timestamp, line]` pairs. The timestamp is in **nanoseconds** since 1970:

```sh
NOW=$(python3 -c 'import time; print(time.time_ns())')
curl -s -w '%{http_code}\n' -H 'Content-Type: application/json' \
  -X POST http://127.0.0.1:3100/loki/api/v1/push \
  --data "{\"streams\":[{\"stream\":{\"service\":\"tutorial-test\",\"level\":\"info\"},\"values\":[[\"$NOW\",\"hello from part 7\"]]}]}"
```

`204` means accepted. This push API is exactly what Alloy will use in Part 8.

**3. Read it back:**

```sh
curl -sG http://127.0.0.1:3100/loki/api/v1/query_range \
  --data-urlencode 'query={service="tutorial-test"}' | python3 -m json.tool | head -20
```

You'll find your line, with your two labels plus two Loki added by itself: `service_name` (Loki copies a service label into it, a convention its own UI relies on) and `detected_level` (Loki guesses the level from labels or the text).

**4. Loki's retention is really on.** Loki shows its running configuration:

```sh
curl -s http://127.0.0.1:3100/config | grep -E 'retention_enabled|retention_period|reject_old_samples'
```

You should see `retention_enabled: true`, `retention_period: 31d` and `reject_old_samples: true`. (A second `retention_period: 0s` belongs to an unused legacy component and can be ignored.)

**5. Prometheus sees Loki:** `up{job="loki"}` is `1`.

## When something goes wrong

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Loki won't start: `invalid compactor config: compactor.delete-request-store should be configured when retention is enabled` | Retention on without a delete store | Add `delete_request_store: filesystem` to `compactor`. |
| The Loki volume grows forever | Retention isn't enforced | Set `compactor.retention_enabled: true`, not just `retention_period`. |
| Push returns `400 ... entry too far behind` | The timestamp is older than `reject_old_samples_max_age` | Expected for old data. Use a current timestamp. |
| Push returns `400 ... structured metadata` errors | Structured metadata is disabled or the schema is older than `v13` | Set `allow_structured_metadata: true` and use `tsdb` with `v13`. |
| Push returns `429` | The rate limit was hit | Something is flooding logs; find it, or raise `ingestion_rate_mb`. |
| `/ready` says the ingester isn't ready | Normal for ~15 seconds after start | Wait. |

## What you have now

- Loki `3.7.8` storing logs on a named volume, with a schema that supports structured metadata.
- Retention that's actually enforced: 31 days, cleaned up by the compactor.
- Protection against floods and stale timestamps.
- Prometheus monitoring Loki.

Loki is empty apart from your test line. In [Part 8](08-ship-container-logs-with-alloy.md) Alloy starts shipping every WispURL container's logs, and cleans them up on the way: parsing JSON, adding labels, redacting secrets, and joining multi-line tracebacks.

## Key takeaways

- Loki indexes labels only. Labels must have few values; IDs belong in structured metadata.
- Use schema `v13` with the `tsdb` store for new installs. Schema entries can only be added, never edited.
- `retention_period` does nothing on its own. The compactor with `retention_enabled: true` does the deleting.
- Size log retention from bytes ingested per day and compression ratio; logs usually cost more than metrics.
- Reject old samples and set ingestion limits so a broken client can't damage the store.
- Single-binary mode with filesystem storage is right for one machine; clusters use object storage.

## FAQ

### Why is Loki not deleting old logs?

Because retention is enforced by the compactor, not by `retention_period` alone. Add a `compactor` block with `retention_enabled: true` and `delete_request_store: filesystem` (or your object store). Expired chunks are then marked on each compaction run and deleted after `retention_delete_delay`.

### What labels should I use in Loki?

Only labels with a small, fixed set of values, such as service, container, environment and log level. Each unique label combination creates a separate stream, so high-cardinality values like request IDs, user IDs or trace IDs should go in structured metadata or stay in the log line itself.

### What is structured metadata in Loki?

Key-value pairs attached to individual log lines and stored alongside them, but not added to the index. They let you filter on values like `trace_id` without the cost of making them labels. It requires schema `v13` with the `tsdb` store and `allow_structured_metadata: true`.

### How do I send a test log line to Loki?

POST JSON to `/loki/api/v1/push` with a `streams` array. Each stream has a `stream` object of labels and a `values` array of `[timestamp_in_nanoseconds, "log line"]` pairs. A `204` response means the line was accepted.

### Should I run Loki in single binary or microservices mode?

Single binary for one machine or modest volumes: simplest to run, everything in one process. Microservices or "simple scalable" mode when you need to scale reads and writes independently across many machines, which also requires object storage.

---

**Series navigation:** Previous: [Part 6, Deploy Grafana](06-deploy-grafana.md) · [Series index](README.md) · Next: [Part 8, Ship Container Logs with Alloy](08-ship-container-logs-with-alloy.md)
