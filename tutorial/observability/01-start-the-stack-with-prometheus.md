---
title: "Observability for WispURL, Part 1: Start the Stack with Prometheus"
seo_title: "Run Prometheus with Docker Compose: Step-by-Step"
slug: prometheus-docker-compose-setup
description: "Run Prometheus with Docker Compose: pin the version, size retention, bind to localhost, add a healthcheck and log rotation, and run your first PromQL query."
series: "Observability for WispURL"
part: 1
date: 2026-10-17
last_updated: 2026-10-17
author: David Essien
tags: [prometheus, docker-compose, metrics, observability]
keywords:
  - "Prometheus Docker Compose"
  - "Prometheus setup"
  - "Prometheus retention size"
  - "promtool check config"
  - "Prometheus healthcheck"
  - "Docker log rotation"
  - "PromQL basics"
difficulty: beginner
estimated_time: 30 minutes
prerequisites:
  - "Part 0: What We're Building"
  - "WispURL running with Docker Compose (README steps 1 to 6)"
repo_files:
  - compose.observability.yaml
  - observability/prometheus/prometheus.yml
---

# Observability for WispURL, Part 1: Start the Stack with Prometheus

> **In short:** to run Prometheus with Docker Compose, put it in its own Compose project, pin an exact image version (`prom/prometheus:v3.15.0`), cap storage by both time and size (`15d` and `5GB`), bind its port to `127.0.0.1`, enable the remote-write receiver for collectors, add a `wget` healthcheck and log rotation, and validate every config change with `promtool` before applying it.

Every other tool in this series sends data to something, so we start with the thing that stores it. In this part you will:

1. create a separate Compose file for observability tools;
2. add Prometheus to it, pinned to an exact version;
3. limit how much disk Prometheus can use;
4. give it a healthcheck and log rotation;
5. tell it what to scrape;
6. start it and query it.

At the end, Prometheus is running at http://127.0.0.1:9090 and collecting its own metrics. Nothing from WispURL yet: that comes in Parts 2 and 3.

## What Prometheus does

Prometheus is a database for numbers that change over time. Each number has a name and a set of labels, for example:

```text
http_requests_total{service="shortener-service", path="/links/{short_code}", status="200"}  4213
```

Prometheus usually gets data by **scraping**: every few seconds it makes an HTTP request to a target's `/metrics` page and stores whatever numbers it finds. It can also **receive** data that another program pushes to it, which is called **remote write**. We'll use both:

- Prometheus scrapes itself and, later, the other observability tools.
- Grafana Alloy scrapes the WispURL services and pushes the results to Prometheus with remote write (Part 3).

## Why Prometheus?

Before writing any config, it's worth knowing what else you could use and why Prometheus wins here.

| Option | How it works | Why not here |
| --- | --- | --- |
| **Graphite** | Metrics named like paths (`shortener.redirects.200`) | No labels, so you can't slice by service, route and status at once. Largely superseded. |
| **InfluxDB** | Time-series database, usually push-based, with its own query language | Good database, but a smaller ecosystem of ready-made exporters and dashboards than Prometheus. |
| **VictoriaMetrics** | Prometheus-compatible, more storage-efficient | A strong choice at scale. It speaks PromQL and remote write, so you could swap it in later without changing anything else. |
| **Mimir, Thanos, Cortex** | Horizontally scalable, long-term storage built around Prometheus | Built for clusters and years of data. Overkill for one machine. |
| **CloudWatch, Datadog** | Managed services | Cost per metric, and you learn less about how metrics work. |

Prometheus is the default choice for a few concrete reasons:

- **Ecosystem.** Nearly every piece of infrastructure (PostgreSQL, Redis, RabbitMQ, Kubernetes, Grafana, Loki itself) exposes metrics in the Prometheus format. Most of our dependency monitoring in Part 4 is a few lines of config.
- **Labels and PromQL.** A metric like `http_requests_total` carries labels (`service`, `path`, `status`), and PromQL lets you slice and combine them freely: error ratio per service, latency per route, and so on.
- **Alerting built in.** Prometheus evaluates alert rules itself (Part 15).
- **Simple to run.** One binary, one folder of data, no cluster.

It also has limits you should design around:

- **It's a single node.** If it's down, you have no metrics. Production runs two copies or uses a managed or replicated system.
- **It's not long-term storage.** It's designed for weeks of data, not years.
- **It hates unbounded labels.** Every unique combination of label values is a separate **time series** held in memory. A label like `user_id` or a raw URL path can create millions of series and take Prometheus down. Part 2 shows exactly this mistake and its fix.
- **It stores numbers, not events.** "Which user hit this error?" is a question for logs or traces, not metrics.

## Step 1: Create the folders

From the root of the WispURL repository:

```sh
mkdir -p observability/prometheus
```

Each tool gets its own folder under `observability/`. Prometheus's configuration file goes in `observability/prometheus/`. In Part 15 we'll add alert rules to the same folder.

## Step 2: Start the Compose file

Create `compose.observability.yaml` in the repository root, next to `docker-compose.yml`:

```yaml
name: observability

# Cap every container's on-disk log at 3 x 10 MB. Alloy reads the same logs
# through the Docker API, so rotating them locally loses nothing.
x-logging: &default-logging
  driver: json-file
  options:
    max-size: "10m"
    max-file: "3"

services:
  # The Prometheus service goes here (Step 3).

networks:
  observability:
    driver: bridge

volumes:
  prometheus-data:
```

What each part does:

- **`name: observability`** gives this Compose project its own name. Its containers, networks and volumes are prefixed with `observability`, so they never collide with the application's (prefixed `wispurl`). You can stop or wipe one project without touching the other.
- **`x-logging`** is a reusable block. Any top-level key starting with `x-` is ignored by Compose, so it's a safe place to define shared settings. The `&default-logging` part names it so services can refer to it later with `*default-logging`.
  - Docker's default log driver keeps every line a container ever printed, forever. A busy container can fill your disk. `max-size: "10m"` and `max-file: "3"` keep at most three 10 MB files per container and delete the oldest.
- **`networks.observability`** is a private network for the observability tools. Only the collector (Alloy, Part 3) will also join the application's network.
- **`volumes.prometheus-data`** is a named volume where Prometheus stores its data. Named volumes survive `docker compose down`, so you don't lose metrics when you restart.

> In the finished repository this skeleton is `compose.observability.yaml` lines 1–11 (the header) and lines 213–227 (networks and volumes). Later parts add more networks, volumes and a `secrets` section.

## Step 3: Add the Prometheus service

Replace the `# The Prometheus service goes here` comment with this block:

```yaml
  prometheus:
    image: ${PROMETHEUS_IMAGE:-prom/prometheus:v3.15.0}
    restart: unless-stopped
    container_name: prometheus
    command:
      - --config.file=/etc/prometheus/prometheus.yml
      - --storage.tsdb.path=/prometheus
      - --storage.tsdb.retention.time=${PROMETHEUS_RETENTION_TIME:-15d}
      - --storage.tsdb.retention.size=${PROMETHEUS_RETENTION_SIZE:-5GB}
      - --web.enable-remote-write-receiver
      - --web.enable-lifecycle
    ports:
      - "127.0.0.1:${PROMETHEUS_PORT:-9090}:9090"
    volumes:
      - ./observability/prometheus:/etc/prometheus:ro
      - prometheus-data:/prometheus
    networks:
      - observability
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:9090/-/healthy"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 15s
    logging: *default-logging
```

> This is `compose.observability.yaml` lines 12–36 in the finished repository.

Let's go through it.

### The image: always pin a version

```yaml
image: ${PROMETHEUS_IMAGE:-prom/prometheus:v3.15.0}
```

`v3.15.0` is an exact release. Never use `latest` for infrastructure: `latest` changes whenever the maintainers publish, so two people running "the same" file can get different software, and a routine restart can quietly upgrade you into a breaking change.

The `${PROMETHEUS_IMAGE:-...}` wrapper reads a `PROMETHEUS_IMAGE` environment variable and falls back to the pinned tag when it isn't set. That lets you try a new version without editing the file:

```sh
PROMETHEUS_IMAGE=prom/prometheus:v3.16.0 docker compose -f compose.observability.yaml up -d prometheus
```

To find versions, open https://hub.docker.com/r/prom/prometheus/tags and filter by the version. Prometheus tags start with `v`.

### The command flags

| Flag | Why |
| --- | --- |
| `--config.file=/etc/prometheus/prometheus.yml` | Where to read the scrape configuration (Step 4). |
| `--storage.tsdb.path=/prometheus` | Where to store data. This path is the named volume. |
| `--storage.tsdb.retention.time=15d` | Delete data older than 15 days. |
| `--storage.tsdb.retention.size=5GB` | Also delete the oldest data once the database passes 5 GB, whichever limit is hit first. Without a size limit, a sudden flood of metrics could still fill the disk inside 15 days. |
| `--web.enable-remote-write-receiver` | Accept metrics pushed to `/api/v1/write`. Alloy (Part 3) and Tempo (Part 9) push this way. It's off by default. |
| `--web.enable-lifecycle` | Allow `POST /-/reload` to reload the config without a restart. |

The `${...:-15d}` and `${...:-5GB}` defaults work the same way as the image: you can override them from your shell or an `.env` file.

### How the retention numbers were chosen

Retention is a trade-off between how far back you can look and how much disk you spend. Here is how to size it rather than guess.

Prometheus compresses each stored sample to roughly 1–2 bytes. So:

```text
disk per day ≈ samples per second × 86,400 × ~1.5 bytes
```

You can measure samples per second on a running Prometheus with:

```promql
sum(rate(prometheus_tsdb_head_samples_appended_total[5m]))
```

With the complete WispURL stack from this series (every service, exporter and the host and container metrics), that query returns about **1,240 samples per second**, from about **32,000 series**. That works out as:

```text
1,240 × 86,400 × 1.5 bytes ≈ 160 MB per day
160 MB × 15 days         ≈ 2.4 GB
```

So 15 days fits in about 2.4 GB, and the 5 GB size limit leaves roughly double that as headroom. Why 15 days? Two weeks lets you compare "this week" with "last week", which is how you spot a slow regression. Anything longer is for capacity planning, which belongs in long-term storage, not a local Prometheus.

Re-run the query after adding new exporters. If samples per second doubles, so does your disk use.

### Ports: only on localhost

```yaml
ports:
  - "127.0.0.1:${PROMETHEUS_PORT:-9090}:9090"
```

Writing `127.0.0.1:` in front means the port is only reachable from your own machine. Plain `"9090:9090"` would publish Prometheus on every network interface, so anyone on the same Wi-Fi could read your metrics. Prometheus has no login by default, so keep it on localhost.

### Volumes

```yaml
volumes:
  - ./observability/prometheus:/etc/prometheus:ro
  - prometheus-data:/prometheus
```

- The first line mounts the whole `observability/prometheus` folder into the container, **read-only** (`:ro`). Prometheus never needs to change its own config. We mount the folder, not just the one file, because in Part 15 we'll add a `rules/` subfolder next to `prometheus.yml`.
- The second line stores the database in the named volume.

### The healthcheck

```yaml
healthcheck:
  test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:9090/-/healthy"]
```

Docker runs this command inside the container every 30 seconds. `/-/healthy` returns 200 when Prometheus is working, and `wget --spider` checks the URL without downloading anything. Three failures in a row mark the container `unhealthy`. Other services can then wait for Prometheus to be healthy before starting (we'll use that in Part 3).

A healthcheck can only use programs that exist inside the image. Before writing one, check:

```sh
docker run --rm --entrypoint sh prom/prometheus:v3.15.0 -c 'command -v wget curl'
```

The Prometheus image has `wget` but not `curl`, so we use `wget`. Some images we'll meet later have neither, and we'll handle that when we get there.

### `restart`, `container_name` and `logging`

- `restart: unless-stopped` brings Prometheus back after a crash or a Docker restart, unless you stopped it yourself.
- `container_name: prometheus` gives the container a fixed, short name, handy for `docker logs prometheus`.
- `logging: *default-logging` applies the rotation block from Step 2.

## Step 4: Tell Prometheus what to scrape

Create `observability/prometheus/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  scrape_timeout: 10s
  evaluation_interval: 15s

scrape_configs:
  # Prometheus's own operational metrics.
  - job_name: prometheus
    static_configs:
      - targets:
          - localhost:9090
        labels:
          environment: docker
          application: observability
```

> This is `observability/prometheus/prometheus.yml` lines 1–14 in the finished repository.

- **`scrape_interval: 15s`**: fetch every target every 15 seconds. This one number drives detail, storage and load together:

  | Interval | Detail | Storage (relative) | When to use |
  | --- | --- | --- | --- |
  | 5s | Catches very short spikes | 3× | Debugging a specific latency problem |
  | **15s** | Good for dashboards and alerts | 1× | **Default for most systems** |
  | 60s | Smooths out spikes | 0.25× | Slow-changing things like disk usage, or very large fleets |

  Alerts usually look at windows of several minutes (`rate(...[5m])`), so 15 seconds gives plenty of data points per window. Keep one interval everywhere if you can: mixing intervals makes `rate()` windows harder to reason about.
- **`scrape_timeout: 10s`**: give up on a slow target after 10 seconds. It must be shorter than the interval.
- **`evaluation_interval: 15s`**: how often alert rules are checked (Part 15).
- **`scrape_configs`** is a list of **jobs**. A job is a group of targets scraped the same way. Our first job scrapes Prometheus itself at `localhost:9090`; inside the container, Prometheus is listening on that address.
- **`labels`** are added to every series this job produces. Labels like `application: observability` let you tell the monitoring tools' own metrics apart from WispURL's later.

### Validate before you start

Prometheus ships a checker called `promtool`. Run it from the image so you don't have to install anything:

```sh
docker run --rm \
  -v "$PWD/observability/prometheus:/etc/prometheus:ro" \
  --entrypoint promtool prom/prometheus:v3.15.0 \
  check config /etc/prometheus/prometheus.yml
```

You should see:

```text
 SUCCESS: /etc/prometheus/prometheus.yml is valid prometheus config file syntax
```

Make this a habit: validate every config change before applying it.

## Step 5: Start Prometheus

```sh
docker compose -f compose.observability.yaml up -d
```

The `-f` flag points Compose at our second file. Without it, Compose would use `docker-compose.yml`, the application.

Check the status:

```sh
docker compose -f compose.observability.yaml ps
```

After about 15 seconds the status should read `Up ... (healthy)`. If it says `(health: starting)`, wait a little longer.

## Check that it works

Open http://127.0.0.1:9090. This is Prometheus's built-in UI.

**1. Is the target being scraped?** Go to **Status → Target health**. You should see the `prometheus` job with one target in state **UP**.

**2. Run your first query.** On the **Query** page, enter:

```promql
up
```

and press **Execute**. You'll get one result with the value `1`:

```text
up{application="observability", environment="docker", instance="localhost:9090", job="prometheus"}  1
```

`up` is a series Prometheus creates for every target on every scrape: `1` if the scrape worked, `0` if it failed. It's the simplest health signal there is, and our first alert in Part 15 is built on it.

**3. Look at some real data.** Try these and switch to the **Graph** tab:

```promql
prometheus_tsdb_head_series
```

how many different time series Prometheus holds in memory right now, and

```promql
rate(prometheus_http_requests_total[5m])
```

how many HTTP requests per second Prometheus itself is handling, per endpoint. `rate(...[5m])` turns an ever-growing counter into a per-second rate averaged over five minutes. You'll use `rate()` constantly.

**4. Confirm the retention settings.** Go to **Status → Command-line flags** and search for `retention`. You should see `storage.tsdb.retention.time` set to `15d` and `storage.tsdb.retention.size` set to `5GiB`. Prometheus treats `GB` as base-2 (1 GB = 1024³ bytes), so it displays the value as `5GiB`.

**5. Reload without restarting.** Change something harmless in `prometheus.yml` (for example the `application` label), validate it with `promtool`, then:

```sh
curl -X POST http://127.0.0.1:9090/-/reload
```

Run `up` again and the label has changed. This works because of `--web.enable-lifecycle`.

## When something goes wrong

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `docker compose up` says `no configuration file provided` | You forgot `-f compose.observability.yaml` | Add the flag. |
| Container keeps restarting | A config error | `docker logs prometheus`; the first error line names the problem. Run `promtool` on the file. |
| Status stays `unhealthy` | Prometheus started but `/-/healthy` fails | `docker logs prometheus`. Check that port 9090 isn't used by something else. |
| Browser can't reach http://127.0.0.1:9090 | Port in use or container down | `docker compose -f compose.observability.yaml ps`; change `PROMETHEUS_PORT` if 9090 is taken. |
| A change to `prometheus.yml` has no effect | Prometheus reads its config only at start or on reload | `curl -X POST http://127.0.0.1:9090/-/reload`. |

One thing to know about Docker Compose: `docker compose up -d` only recreates a container when its definition in the Compose file changes. Editing a mounted config file isn't such a change. For config-only edits, reload (Prometheus) or `docker compose -f compose.observability.yaml restart <service>` (other tools).


## What you have now

- A separate `observability` Compose project with log rotation built in.
- Prometheus pinned to `v3.15.0`, bound to localhost, keeping at most 15 days or 5 GB of data.
- A healthcheck other services can wait on.
- Remote write switched on and ready for Alloy.

Prometheus is only watching itself so far. In [Part 2](02-expose-red-metrics-from-the-services.md) we make the WispURL services expose useful metrics: how many requests each route gets, how many fail, and how long they take.

## Key takeaways

- Pin infrastructure images to exact versions; `latest` changes underneath you.
- Set both `retention.time` and `retention.size`: time gives a predictable look-back, size protects the disk from sudden metric floods.
- Size retention from measured ingestion: samples per second × 86,400 × about 1.5 bytes per sample per day.
- Bind monitoring ports to `127.0.0.1`; Prometheus has no login by default.
- Healthchecks can only use binaries inside the image, so check what exists before writing one.
- Validate with `promtool check config` and reload with `POST /-/reload` instead of restarting.

## FAQ

### How do I run Prometheus with Docker Compose?

Add a service using a pinned image such as `prom/prometheus:v3.15.0`, mount your `prometheus.yml` read-only into `/etc/prometheus`, store data in a named volume at `/prometheus`, publish port 9090 on `127.0.0.1`, and start it with `docker compose -f <file> up -d`. The full service definition is in Step 3 of this article.

### How do I limit Prometheus disk usage?

Use both `--storage.tsdb.retention.time` (for example `15d`) and `--storage.tsdb.retention.size` (for example `5GB`). Prometheus deletes the oldest data when either limit is reached. Size the values from your measured ingestion rate.

### How much disk does Prometheus need?

Roughly samples per second × 86,400 × 1–2 bytes per day. Measure samples per second with `sum(rate(prometheus_tsdb_head_samples_appended_total[5m]))`. A stack of about 32,000 series ingesting about 1,240 samples per second uses around 160 MB per day.

### Why enable the Prometheus remote-write receiver?

`--web.enable-remote-write-receiver` lets other programs push metrics to Prometheus at `/api/v1/write`. Collectors such as Grafana Alloy and Tempo's metrics generator use it. It's disabled by default.

### How do I reload the Prometheus configuration without restarting?

Start Prometheus with `--web.enable-lifecycle`, then send `curl -X POST http://127.0.0.1:9090/-/reload`. Validate the file with `promtool check config` first, because a reload with an invalid file is rejected.

---

**Series navigation:** Previous: [Part 0, What We're Building](00-the-observability-plan.md) · [Series index](README.md) · Next: [Part 2, Expose RED Metrics from the Services](02-expose-red-metrics-from-the-services.md)
