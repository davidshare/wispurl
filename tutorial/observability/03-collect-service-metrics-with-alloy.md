---
title: "Observability for WispURL, Part 3: Collect Service Metrics with Grafana Alloy"
seo_title: "Grafana Alloy Docker Discovery to Prometheus Remote Write"
slug: grafana-alloy-docker-metrics-remote-write
description: "Deploy Grafana Alloy with Docker Compose to discover containers by label, scrape their metrics, and push them to Prometheus with remote write."
series: "Observability for WispURL"
part: 3
date: 2026-10-17
last_updated: 2026-10-17
author: David Essien
tags: [grafana-alloy, prometheus, service-discovery, relabeling, docker-compose]
keywords:
  - "Grafana Alloy tutorial"
  - "Alloy discovery.docker"
  - "Prometheus relabel_configs explained"
  - "Prometheus remote write"
  - "Docker service discovery Prometheus"
  - "Alloy healthcheck"
  - "Docker socket security"
difficulty: intermediate
estimated_time: 45 minutes
prerequisites:
  - "Part 2: Expose RED Metrics from the Services"
repo_files:
  - compose.observability.yaml
  - observability/alloy/config.alloy
  - observability/prometheus/prometheus.yml
  - docker-compose.yml
---

# Observability for WispURL, Part 3: Collect Service Metrics with Grafana Alloy

> **In short:** Grafana Alloy watches the Docker API for containers, keeps only those on the application network that carry a `prometheus.io/scrape=true` label, scrapes each container's `/metrics` by its own IP address, and pushes the results into Prometheus with remote write. Services opt in with three labels in `docker-compose.yml`, so adding a new service needs no change to the monitoring config. Prometheus scrapes Alloy directly, so if the collector dies you find out.

The services now expose metrics (Part 2) and Prometheus is ready to store them (Part 1). In this part we connect the two with **Grafana Alloy**, the collector that will eventually handle logs and traces too. You will:

1. learn how Alloy's configuration works;
2. let services opt in to monitoring with Docker labels;
3. make Alloy discover them automatically;
4. use **relabeling** to turn Docker metadata into clean Prometheus labels;
5. push the metrics into Prometheus;
6. run Alloy in Compose with a healthcheck that works in its minimal image.

## How Alloy works

An Alloy configuration is a set of **components** wired together, a bit like Unix pipes. Each component does one job, takes **arguments**, and **exports** values that other components can use:

```text
discovery.docker  →  discovery.relabel  →  prometheus.scrape  →  prometheus.remote_write  →  Prometheus
 (find containers)    (filter + label)       (fetch /metrics)       (push)
```

A component looks like this:

```alloy
prometheus.remote_write "prometheus" {
  endpoint {
    url = "http://prometheus:9090/api/v1/write"
  }
}
```

- `prometheus.remote_write` is the component **type**.
- `"prometheus"` is a **label** you choose. Together they form its name, `prometheus.remote_write.prometheus`.
- Other components refer to its exports by that name, for example `prometheus.remote_write.prometheus.receiver`.

Alloy works out the order to start things from these references, and re-evaluates a component whenever its inputs change. When a new container starts, the discovery component's output changes, and the scrape component picks up the new target without a restart.

## Design decisions

### Discover targets instead of listing them

You could list every service in a static scrape config. That works until someone adds a service and forgets to update monitoring. With **discovery**, Alloy asks Docker which containers exist and builds the target list itself.

### Opt in with labels, not "scrape everything"

Not every container has a `/metrics` page: Postgres, the frontend and Vault don't. Scraping them would just produce failed targets. So a container only gets scraped if it **opts in** with labels:

```yaml
prometheus.io/scrape: "true"
prometheus.io/port: "8000"
prometheus.io/path: /metrics
```

This puts the decision with the people who own the service. Kubernetes users will recognise the pattern: it's the same `prometheus.io/*` convention widely used for pod annotations.

### Filter by network

A developer machine often runs several projects at once. Alloy keeps only containers on the WispURL network, so it never scrapes or reads anything from unrelated projects.

### Scrape each container's IP, not its service name

The obvious target address is the Compose service name, `auth-service:8000`. But if you scale a service to three replicas, that name resolves to *any one* of them, so each scrape samples a random replica and you can't see them individually. We scrape each container's own IP address on the network instead, so every replica is a separate target.

The IP changes whenever a container is recreated, so we don't use it as the target's identity. We set the `instance` label to the **container name**, which stays the same across restarts. Otherwise every restart would start a new set of series.

### Push to Prometheus, but let Prometheus watch Alloy

Alloy pushes everything it scrapes to Prometheus with remote write. That has a side effect worth understanding: these targets **won't appear on Prometheus's Targets page**, because Prometheus isn't the one scraping them. Instead, Alloy writes an `up` series for each target, so `up{job="docker-compose-services"}` still tells you which services are healthy.

But if Alloy itself dies, all those series simply stop arriving. Nothing says "down". So Prometheus scrapes **Alloy directly**: if Alloy stops, `up{job="alloy"}` turns to 0. Monitoring the monitoring is called **meta-monitoring**. In Part 15 we add an alert for the case where Alloy is up but nothing is arriving.

### The Docker socket is powerful, and `:ro` doesn't change that

To discover containers, Alloy needs the Docker API, which means mounting `/var/run/docker.sock`. Be clear about what that gives it: the Docker API can start containers, mount the host's disk and run commands. Mounting the socket with `:ro` only stops the container from replacing the socket *file*. **Every API call still works.** Anyone who can change Alloy's config, or exploit Alloy, effectively has root on the host.

On a developer laptop that's an acceptable trade. On a shared server you would put a **socket proxy** in between, such as `tecnativa/docker-socket-proxy`, which only allows the read-only API endpoints Alloy needs. In Kubernetes the problem disappears: Alloy discovers pods through the Kubernetes API with a read-only service account.

## Step 1: Label the services

In `docker-compose.yml`, define the labels once as a YAML anchor near the top:

```yaml
# Alloy scrapes /metrics from containers that carry these labels.
x-prometheus-labels: &prometheus-labels
  prometheus.io/scrape: "true"
  prometheus.io/port: "8000"
  prometheus.io/path: /metrics
```

> `docker-compose.yml` lines 6–10.

Then merge them into each of the six HTTP services (auth, shortener, analytics, gateway, qr, rate-limiter):

```yaml
  auth-service:
    # ...
    labels:
      <<: [*prometheus-labels, *python-log-labels]
```

> For example `docker-compose.yml` lines 108–109. The `*python-log-labels` anchor is used for logs in Part 8; until then, `<<: *prometheus-labels` is enough.

The labels use **map** syntax (`key: value`), not list syntax (`- "key=value"`). YAML can merge maps from several anchors with `<<: [...]`, but it can't join lists. Map syntax lets a service combine the metrics labels with other label sets later.

Recreate the services so Docker applies the labels (no rebuild needed):

```sh
docker compose up -d
```

Check one:

```sh
docker inspect wispurl-gateway-1 --format '{{json .Config.Labels}}' | python3 -m json.tool | grep prometheus
```

## Step 2: Write the Alloy pipeline

Create `observability/alloy/config.alloy`. It has three sections for now.

### 2a. Where to send metrics

```alloy
prometheus.remote_write "prometheus" {
  endpoint {
    url = "http://prometheus:9090/api/v1/write"
  }
}
```

> `config.alloy` lines 5–9.

This is the receiving end of `--web.enable-remote-write-receiver` from Part 1. `prometheus` is the Prometheus container's name on the `observability` network. Remote write buffers samples in a write-ahead log on disk, so if Prometheus restarts, Alloy holds the data and sends it once Prometheus is back.

### 2b. Find containers

```alloy
discovery.docker "containers" {
  host = "unix:///var/run/docker.sock"
}
```

> `config.alloy` lines 16–18.

This asks the Docker API for all running containers and refreshes the list every minute (the default `refresh_interval`). It produces one **target** per container, per network and per exposed port, each carrying metadata labels such as:

| Label | Example |
| --- | --- |
| `__meta_docker_container_name` | `/wispurl-gateway-1` |
| `__meta_docker_network_name` | `wispurl_wispurl-network` |
| `__meta_docker_network_ip` | `172.18.0.12` |
| `__meta_docker_container_label_prometheus_io_scrape` | `true` |
| `__meta_docker_container_label_com_docker_compose_service` | `gateway` |

Container labels become `__meta_docker_container_label_<name>`, with dots and slashes turned into underscores: `prometheus.io/scrape` becomes `prometheus_io_scrape`.

A one-minute refresh means a new container is scraped within about a minute of starting. Shorten `refresh_interval` if you need faster pickup, at the cost of more Docker API calls.

### 2c. Filter and label: relabeling

**Relabeling** is how Prometheus-style systems turn raw discovery metadata into the targets and labels you actually want. Each `rule` reads some labels, matches a regular expression, and then does one of a few things:

| Action | Effect |
| --- | --- |
| `keep` | Keep the target only if the regex matches; drop it otherwise |
| `drop` | Drop the target if the regex matches |
| `replace` (default) | Write `replacement` into `target_label`, with `$1`, `$2` filled from the regex groups |

Two details that trip people up:

- When `source_labels` lists several labels, their values are joined with `;` before matching. That's why one rule below matches `^(.+);([0-9]+)$`.
- Labels starting with `__` are temporary: they're available during relabeling and then thrown away. `__address__` (where to scrape) and `__metrics_path__` (which path) are special: they control the scrape itself.

Here are the rules, in order:

```alloy
discovery.relabel "metrics" {
  targets = discovery.docker.containers.targets

  // 1. Keep only containers on the app network
  rule {
    source_labels = ["__meta_docker_network_name"]
    regex         = sys.env("WISPURL_NETWORK")
    action        = "keep"
  }

  // 2. Keep only containers marked for scraping
  rule {
    source_labels = ["__meta_docker_container_label_prometheus_io_scrape"]
    regex         = "^true$"
    action        = "keep"
  }

  // 3. Keep only containers with a valid port label
  rule {
    source_labels = ["__meta_docker_container_label_prometheus_io_port"]
    regex         = "^[0-9]+$"
    action        = "keep"
  }

  // 4. Drop IPv6 port bindings to prevent duplicate targets per container
  rule {
    source_labels = ["__meta_docker_port_public_ip"]
    regex         = "^::$"
    action        = "drop"
  }

  // 5. Scrape the container's own IP on the app network (e.g. 172.18.0.7:8000).
  rule {
    source_labels = [
      "__meta_docker_network_ip",
      "__meta_docker_container_label_prometheus_io_port",
    ]
    regex        = "^(.+);([0-9]+)$"
    target_label = "__address__"
    replacement  = "$1:$2"
  }

  // 6. Honour a custom prometheus.io/path.
  rule {
    source_labels = ["__meta_docker_container_label_prometheus_io_path"]
    regex         = "^(/.+)$"
    target_label  = "__metrics_path__"
    replacement   = "$1"
  }

  // 7. Clean container name, and use it as the stable instance identity
  rule {
    source_labels = ["__meta_docker_container_name"]
    regex         = "^/(.+)$"
    target_label  = "container"
    replacement   = "$1"
  }

  rule {
    source_labels = ["__meta_docker_container_name"]
    regex         = "^/(.+)$"
    target_label  = "instance"
    replacement   = "$1"
  }

  // 8. Compose service name, plus static labels
  rule {
    source_labels = ["__meta_docker_container_label_com_docker_compose_service"]
    regex         = "^(.+)$"
    target_label  = "compose_service"
    replacement   = "$1"
  }

  rule {
    target_label = "environment"
    replacement  = "docker"
  }

  rule {
    target_label = "application"
    replacement  = "wispurl"
  }
}
```

> `config.alloy` lines 30–117 (shortened slightly here; the file has more comments).

What each rule is for:

1. **Network filter.** `sys.env("WISPURL_NETWORK")` reads an environment variable that Compose passes in (Step 3). The network name is defined once, in `compose.observability.yaml`, and both Compose and Alloy use it. If you rename the project, you change one value.
2. **Opt-in check.** No `prometheus.io/scrape=true` label, no scrape.
3. **Port check.** Guards against a typo like `prometheus.io/port: "http"`.
4. **Duplicate guard.** A container that publishes a port to the host is listed once per host binding (IPv4 `0.0.0.0` and IPv6 `::`). After rule 5 those entries would point at the same address, so we drop the IPv6 copy.
5. **Address.** Container IP plus the declared port, for the reasons in *Design decisions*.
6. **Path.** Use the container's declared path. Note the capture group `(/.+)`: `$1` copies what the group matched. Without parentheses, `$1` is empty, the label is dropped, and the scrape silently falls back to the default `/metrics`, so a service on any other path would never be scraped correctly.
7. **Identity.** `container` and `instance` both get the container name without the leading slash.
8. **Context.** `compose_service`, plus constant labels that identify the environment and application. Constant labels look pointless on one laptop, but they matter the moment two environments send data to the same place.

### 2d. Scrape and forward

```alloy
prometheus.scrape "docker_services" {
  targets         = discovery.relabel.metrics.output
  job_name        = "docker-compose-services"
  metrics_path    = "/metrics"
  scrape_interval = "15s"
  scrape_timeout  = "10s"
  forward_to      = [prometheus.remote_write.prometheus.receiver]
}
```

> `config.alloy` lines 119–126.

`targets` takes the relabeled list; `forward_to` sends every sample to the remote-write component. `job_name` becomes the `job` label on every series, and it's what alerts will use to find these targets. The interval and timeout match Prometheus's global settings from Part 1, so all data has the same resolution.

### Validate the config

Alloy can check a file without running it:

```sh
docker run --rm -e WISPURL_NETWORK=wispurl_wispurl-network \
  -v "$PWD/observability/alloy:/c:ro" \
  grafana/alloy:v1.20.1 validate /c/config.alloy && echo valid
```

The `-e` flag is needed because the config reads `WISPURL_NETWORK`. `alloy fmt /c/config.alloy` prints the file in Alloy's standard formatting, so you can see whether yours matches.

## Step 3: Add Alloy to the Compose file

Add this service to `compose.observability.yaml`, after Prometheus:

```yaml
  alloy:
    image: ${ALLOY_IMAGE:-grafana/alloy:v1.20.1}
    restart: unless-stopped
    command:
      - run
      - --server.http.listen-addr=0.0.0.0:12345
      - --storage.path=/var/lib/alloy/data
      - /etc/alloy/config.alloy
    environment:
      # config.alloy reads this to know which Docker network holds the app.
      WISPURL_NETWORK: ${WISPURL_NETWORK:-wispurl_wispurl-network}
    ports:
      - "127.0.0.1:${ALLOY_UI_PORT:-12345}:12345"
    volumes:
      - ./observability/alloy/config.alloy:/etc/alloy/config.alloy:ro
      - alloy-data:/var/lib/alloy/data
      # Docker API: container discovery (and later, logs and container metrics).
      # Warning: ":ro" on a socket only stops the file being replaced; the API
      # itself stays fully usable. Whoever controls Alloy can control every
      # container on this host. Acceptable on a laptop, not on a shared server.
      - /var/run/docker.sock:/var/run/docker.sock:ro
    depends_on:
      prometheus:
        condition: service_healthy
    networks:
      - observability
      - wispurl-network
    healthcheck:
      # The Alloy image has bash but no wget/curl/nc, so speak HTTP over /dev/tcp.
      test:
        - CMD
        - bash
        - -c
        - exec 3<>/dev/tcp/127.0.0.1/12345 && printf 'GET /-/ready HTTP/1.0\r\n\r\n' >&3 && head -1 <&3 | grep -q ' 200 '
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 15s
    logging: *default-logging
```

> The finished version is `compose.observability.yaml` lines 80–136. Later parts add OTLP ports, host mounts for system metrics, a database secret, and dependencies on Loki and Tempo.

And at the bottom of the file, add the application network and a volume:

```yaml
networks:
  observability:
    driver: bridge

  wispurl-network:
    external: true
    name: ${WISPURL_NETWORK:-wispurl_wispurl-network}

volumes:
  prometheus-data:
  alloy-data:
```

> `compose.observability.yaml` lines 213–227.

The decisions in this block:

- **`--server.http.listen-addr=0.0.0.0:12345`** serves Alloy's UI, its own metrics and its health endpoint. The default listens on `127.0.0.1` *inside* the container, which nothing outside the container can reach. `0.0.0.0` makes it reachable on the Docker networks; the published port is still bound to the host's `127.0.0.1`.
- **`--storage.path` with a named volume** keeps Alloy's state across restarts: the remote-write buffer now, and log read positions in Part 8. Without it, a restart would lose buffered samples and re-read logs.
- **`external: true`** means "this network already exists; don't create or delete it". The application's Compose project creates `wispurl_wispurl-network` (`<project>_<network>`). If the app isn't running, the network doesn't exist and Alloy won't start, so **always start the application first**.
- **Only Alloy joins the app network.** Prometheus and the other tools stay on the private `observability` network. The fewer things that can reach the application, the better.
- **`depends_on: condition: service_healthy`** makes Compose wait for Prometheus's healthcheck before starting Alloy, so the first pushes don't fail.

### Why the healthcheck looks strange

In Part 1 we used `wget` for Prometheus's healthcheck. The Alloy image is minimal: it has **no `wget`, `curl` or `nc`**. A `wget` healthcheck would fail every time and mark a perfectly healthy Alloy as `unhealthy`. You can check for yourself:

```sh
docker run --rm --entrypoint bash grafana/alloy:v1.20.1 -c 'for c in wget curl nc bash; do command -v $c || echo "$c: missing"; done'
```

It does have `bash`, and bash can open a TCP connection itself through the special path `/dev/tcp/<host>/<port>`. The healthcheck uses that to send a tiny HTTP request:

```sh
exec 3<>/dev/tcp/127.0.0.1/12345              # open a TCP connection as file descriptor 3
printf 'GET /-/ready HTTP/1.0\r\n\r\n' >&3      # send an HTTP request on it
head -1 <&3 | grep -q ' 200 '                  # read the status line; succeed only on 200
```

`/-/ready` returns 200 once Alloy has loaded its config. Use this trick for any minimal image that ships bash but no HTTP client.

## Step 4: Let Prometheus watch Alloy

Add a job to `observability/prometheus/prometheus.yml`, under the `prometheus` job:

```yaml
  # Grafana Alloy's own operational metrics and health visibility.
  - job_name: alloy
    metrics_path: /metrics
    static_configs:
      - targets:
          - alloy:12345
        labels:
          environment: docker
          application: observability
```

> `prometheus.yml` lines 16–26.

Validate and reload Prometheus as in Part 1:

```sh
docker run --rm -v "$PWD/observability/prometheus:/etc/prometheus:ro" \
  --entrypoint promtool prom/prometheus:v3.15.0 check config /etc/prometheus/prometheus.yml
curl -X POST http://127.0.0.1:9090/-/reload
```

## Step 5: Start Alloy

Make sure the application is running (`docker compose ps`), then:

```sh
docker compose -f compose.observability.yaml up -d
docker compose -f compose.observability.yaml ps
```

Alloy should reach `Up ... (healthy)` within about 30 seconds.

## Check that it works

**1. The Alloy UI.** Open http://127.0.0.1:12345. Every component is listed with its health. Click `discovery.relabel.metrics` and you'll see its output: one target per HTTP service, with `__address__` set to a container IP and port. Click `prometheus.scrape.docker_services` to see each target's last scrape time and any errors. This page is the first place to look when metrics go missing.

**2. Are the services up?** In Prometheus (http://127.0.0.1:9090), run:

```promql
up{job="docker-compose-services"}
```

You should get six results, all `1`, with `instance` set to container names:

```text
up{application="wispurl", compose_service="gateway", container="wispurl-gateway-1", environment="docker", instance="wispurl-gateway-1", job="docker-compose-services"}  1
...
```

**3. Is real traffic arriving?** Click around the app for a minute, then:

```promql
sum by (service) (rate(http_requests_total[5m]))
```

Switch to the **Graph** tab. One line per service, in requests per second. Your RED metrics from Part 2 are flowing end to end.

**4. Is Alloy itself watched?**

```promql
up{job="alloy"}
```

Should be `1`. Stop Alloy (`docker compose -f compose.observability.yaml stop alloy`) and within 30 seconds this turns to `0`, while the services' `up` series just stop updating. That difference is exactly why Prometheus scrapes Alloy directly. Start it again afterwards.

## When something goes wrong

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `network wispurl_wispurl-network declared as external, but could not be found` | The app isn't running | Start the app first: `docker compose up -d`. |
| Alloy healthy but `up{job="docker-compose-services"}` is empty | No targets survived relabeling | In the Alloy UI, check `discovery.relabel.metrics`. Usually the network name doesn't match `WISPURL_NETWORK`, or the containers weren't recreated after adding labels. |
| Each service appears twice | Duplicate port bindings | Check rule 4, and make sure `instance` comes from the container name. |
| A target's `up` is `0` | The scrape fails | The Alloy UI shows the error on `prometheus.scrape.docker_services`. Often the wrong port or path label. |
| Alloy `unhealthy` but the UI loads | A healthcheck using a tool the image doesn't have | Use the bash `/dev/tcp` check. |
| `permission denied` on `/var/run/docker.sock` (Linux) | Alloy's user can't read the socket | The image runs as root by default. If you changed the user, add it to the socket's group. |
| Services missing from Prometheus's **Targets** page | Expected | Alloy scrapes them, not Prometheus. Query `up{job="docker-compose-services"}` instead. |

## What you have now

- Services opt in to monitoring with three Docker labels.
- Alloy discovers them, filters to the WispURL network, scrapes each container individually, and labels everything consistently.
- Metrics reach Prometheus by remote write, buffered on disk if Prometheus restarts.
- Prometheus watches Alloy, so a dead collector shows up as a down target.

In [Part 4](04-monitor-postgres-redis-rabbitmq.md) we use Alloy's built-in exporters to monitor PostgreSQL, Redis and RabbitMQ, including a read-only database user and per-queue metrics for the dead-letter queue.

## Key takeaways

- Alloy builds pipelines from components; each component's exports feed the next one's arguments.
- Discovery plus opt-in labels means new services are monitored without touching monitoring config.
- Relabeling joins multiple `source_labels` with `;`, anchors regexes, and drops `__` labels afterwards. A `$1` replacement needs a capture group.
- Scrape container IPs so replicas are separate targets; use the container name as `instance` so restarts don't create new series.
- Remote-written targets don't appear on Prometheus's Targets page. Use the `up` series, and scrape the collector itself.
- Mounting the Docker socket `:ro` doesn't make the API read-only. Treat it as root access.

## FAQ

### What is Grafana Alloy?

Grafana Alloy is an open-source telemetry collector from Grafana Labs. It discovers targets, scrapes Prometheus metrics, collects logs and receives OpenTelemetry traces, then forwards each to a backend such as Prometheus, Loki or Tempo. It replaces the older Grafana Agent and Promtail, and embeds OpenTelemetry Collector components.

### How do I discover Docker containers with Grafana Alloy?

Use `discovery.docker` pointed at the Docker socket, filter the targets with `discovery.relabel` (for example by network name and a `prometheus.io/scrape` label), and pass the result to `prometheus.scrape`. The rules in Step 2c are a complete working example.

### Why don't my Alloy targets show up in the Prometheus Targets page?

Because Prometheus isn't scraping them. Alloy scrapes the targets and sends the samples to Prometheus with remote write. Alloy also writes an `up` series per target, so query `up{job="<your job name>"}` to see their health.

### Is it safe to mount the Docker socket read-only?

No more than mounting it read-write. The `:ro` flag only prevents replacing the socket file; the Docker API on the other end still accepts every command, including starting privileged containers. Use a socket proxy that only exposes read-only endpoints on shared machines.

### How do I write a healthcheck for a container without curl or wget?

If the image has bash, open a TCP connection with `/dev/tcp/<host>/<port>`, send a minimal HTTP request with `printf`, and check the status line: `exec 3<>/dev/tcp/127.0.0.1/12345 && printf 'GET /-/ready HTTP/1.0\r\n\r\n' >&3 && head -1 <&3 | grep -q ' 200 '`. If the image has no shell at all, check whether the binary has a built-in health flag, as Loki and Tempo do.

---

**Series navigation:** Previous: [Part 2, Expose RED Metrics from the Services](02-expose-red-metrics-from-the-services.md) · [Series index](README.md) · Next: [Part 4, Monitor PostgreSQL, Redis and RabbitMQ](04-monitor-postgres-redis-rabbitmq.md)
