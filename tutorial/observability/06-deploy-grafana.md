---
title: "Observability for WispURL, Part 6: Deploy Grafana"
seo_title: "Deploy Grafana with Docker Compose and Provisioning"
slug: grafana-docker-compose-provisioning
description: "Run Grafana with Docker Compose, keep the admin password in a Docker secret, and provision the Prometheus data source as code, not by clicking."
series: "Observability for WispURL"
part: 6
date: 2026-10-17
last_updated: 2026-10-17
author: David Essien
tags: [grafana, provisioning, docker-compose, prometheus, infrastructure-as-code]
keywords:
  - "Grafana Docker Compose"
  - "Grafana provisioning datasources"
  - "GF_SECURITY_ADMIN_PASSWORD__FILE"
  - "Grafana Docker secrets"
  - "Grafana Explore PromQL"
  - "Grafana as code"
difficulty: beginner
estimated_time: 30 minutes
prerequisites:
  - "Part 5: Host and Container Metrics"
repo_files:
  - compose.observability.yaml
  - observability/grafana/provisioning/datasources/datasources.yaml
  - observability/prometheus/prometheus.yml
---

# Observability for WispURL, Part 6: Deploy Grafana

> **In short:** run Grafana `13.2.4` in the observability Compose project on `127.0.0.1:3001`, read the admin password from a Docker secret with `GF_SECURITY_ADMIN_PASSWORD__FILE`, disable sign-up and anonymous access, and **provision** data sources from a YAML file with fixed UIDs instead of creating them by hand. The whole Grafana setup then lives in Git and rebuilds identically on any machine.

Prometheus's own UI is good for checking a query, but it's not where you want to spend an incident. **Grafana** is: it graphs metrics from Prometheus, searches logs in Loki, shows traces from Tempo, and links all three. In this part you'll:

1. run Grafana with a secret admin password;
2. connect it to Prometheus **as code**;
3. let Prometheus monitor Grafana;
4. explore the metrics from Parts 2 to 5.

Loki and Tempo are added as data sources in Parts 8 and 9, and dashboards come in Part 14.

## Design decisions

### Why Grafana?

| Option | Strength | Why not here |
| --- | --- | --- |
| Prometheus UI | Built in, nothing to install | Metrics only, no saved dashboards worth the name, no logs or traces |
| Kibana / OpenSearch Dashboards | Excellent for Elasticsearch data | Tied to Elasticsearch; we chose Loki in Part 0 |
| Datadog, New Relic UIs | Polished, all-in-one | Only work with their own hosted backends |
| **Grafana** | Reads Prometheus, Loki, Tempo and dozens of other sources, and links them | Our choice |

The deciding factor is **correlation**. Grafana can turn a trace ID in a log line into a link that opens the trace, and a span in a trace into a link to that service's logs (Part 13). That only works when one tool understands all three backends.

### Provision everything; click nothing

You *can* add a data source by clicking through Grafana's settings. The problem is that the setup then lives only in Grafana's internal database. Delete the volume, move to a new laptop, or set up a teammate's machine, and you're clicking through it all again from memory, slightly differently each time.

Grafana supports **provisioning**: on start-up it reads YAML files from `/etc/grafana/provisioning/` and creates the data sources (and later, dashboards) they describe. The files live in Git, get reviewed like code, and rebuild the same Grafana everywhere. Changes made in the UI to provisioned items can't be saved, which stops the running instance from drifting away from Git.

This is the same idea as infrastructure as code, applied to monitoring.

### Fixed data source UIDs

Every data source has a **UID**. If you let Grafana generate one, it's random, and every dashboard, alert and cross-link that refers to the data source breaks when the UID changes. We set our own: `prometheus`, `loki` and `tempo`. Dashboards in Part 14 and the log-to-trace links in Part 13 depend on them.

### Secure defaults, even locally

| Setting | Value | Why |
| --- | --- | --- |
| Admin password | Read from a Docker secret file | It never appears in the Compose file, in `docker inspect` or in Git |
| `GF_USERS_ALLOW_SIGN_UP` | `false` | Nobody can create their own account |
| `GF_AUTH_ANONYMOUS_ENABLED` | `false` | No access without logging in |
| `GF_ANALYTICS_*` | `false` | No usage reporting or update checks from a private setup |
| Port | `127.0.0.1:3001` | Only reachable from your machine; `3000` is already used by the WispURL frontend |

Grafana's defaults include `admin`/`admin`. Defaults like that end up in production more often than anyone admits, so we never use them.

## Step 1: Create the admin password

```sh
mkdir -p observability/secrets
printf '%s' "$(openssl rand -hex 16)" > observability/secrets/grafana_admin_password.txt
chmod 600 observability/secrets/grafana_admin_password.txt
```

`printf '%s'` writes the password without a trailing newline, the same habit as for the database DSN in Part 4. The `observability/secrets/` folder is git-ignored.

Declare the secret at the bottom of `compose.observability.yaml`, next to `postgres_dsn`:

```yaml
secrets:
  postgres_dsn:
    file: ./observability/secrets/postgres_dsn.txt
  grafana_admin_password:
    file: ./observability/secrets/grafana_admin_password.txt
```

> `compose.observability.yaml` lines 229–233.

## Step 2: Provision the Prometheus data source

Create the folders:

```sh
mkdir -p observability/grafana/provisioning/datasources observability/grafana/dashboards
```

Then `observability/grafana/provisioning/datasources/datasources.yaml`:

```yaml
apiVersion: 1

# Fixed UIDs let dashboards and the cross-links below refer to each data source.
datasources:
  - name: Prometheus
    uid: prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    jsonData:
      timeInterval: 15s
```

> `datasources.yaml` lines 1–12. Parts 8, 9 and 13 add Loki and Tempo to the same file.

- **`access: proxy`** means Grafana's server makes the queries and your browser only talks to Grafana. Prometheus doesn't need to be reachable from the browser, which keeps it on the private network.
- **`url: http://prometheus:9090`** is Prometheus's name on the `observability` Docker network, not `127.0.0.1`. Inside the Grafana container, `127.0.0.1` would be Grafana itself.
- **`isDefault: true`** makes it the data source new panels and Explore start with.
- **`timeInterval: 15s`** tells Grafana how often Prometheus collects data, matching `scrape_interval` from Part 1. Grafana uses it to choose a sensible `$__rate_interval` for `rate()` queries in dashboards, so a range is never shorter than the data's resolution and graphs don't show gaps.

## Step 3: Add the Grafana service

Add to `compose.observability.yaml`:

```yaml
  grafana:
    image: ${GRAFANA_IMAGE:-grafana/grafana:13.2.4}
    restart: unless-stopped
    environment:
      GF_SECURITY_ADMIN_USER: admin
      # Read the admin password from a Docker secret, never from the compose file.
      GF_SECURITY_ADMIN_PASSWORD__FILE: /run/secrets/grafana_admin_password
      GF_USERS_ALLOW_SIGN_UP: "false"
      GF_AUTH_ANONYMOUS_ENABLED: "false"
      GF_ANALYTICS_REPORTING_ENABLED: "false"
      GF_ANALYTICS_CHECK_FOR_UPDATES: "false"
    ports:
      # 3000 is taken by the WispURL frontend.
      - "127.0.0.1:${GRAFANA_PORT:-3001}:3000"
    volumes:
      - ./observability/grafana/provisioning:/etc/grafana/provisioning:ro
      - ./observability/grafana/dashboards:/var/lib/grafana/dashboards:ro
      - grafana-data:/var/lib/grafana
    secrets:
      - grafana_admin_password
    depends_on:
      prometheus:
        condition: service_healthy
    networks:
      - observability
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 30s
    logging: *default-logging
```

> `compose.observability.yaml` lines 138–173. The finished version also waits for Loki and Tempo to be healthy, added in Parts 7 and 9.

And add `grafana-data:` to the `volumes:` list at the bottom.

The parts worth explaining:

- **`GF_<SECTION>_<KEY>` variables** override any setting in Grafana's `grafana.ini`. `GF_SECURITY_ADMIN_USER` is `[security] admin_user`.
- **The `__FILE` suffix** tells Grafana to read the value from a file instead. Any Grafana setting supports it. Combined with the Docker secret, the password is read from `/run/secrets/grafana_admin_password` and never stored in the environment.
- **Three mounts:**
  - provisioning files, read-only;
  - a dashboards folder, read-only (empty for now; Part 14 fills it);
  - a named volume for Grafana's own database: users, preferences, things you explore.
- **Healthcheck.** The Grafana image includes `wget`; `/api/health` returns 200 once Grafana's database is ready.
- **No app network.** Grafana only talks to Prometheus, Loki and Tempo, all on the `observability` network.

## Step 4: Let Prometheus monitor Grafana

Add a job to `prometheus.yml`:

```yaml
  - job_name: grafana
    static_configs:
      - targets:
          - grafana:3000
        labels:
          environment: docker
          application: observability
```

> `prometheus.yml` lines 29–35.

Grafana serves its own metrics at `/metrics` on its normal port: request rates, data-source query errors, dashboard load times. If Grafana goes down during an incident, you want to know.

## Step 5: Start Grafana

```sh
docker compose -f compose.observability.yaml up -d
curl -X POST http://127.0.0.1:9090/-/reload
docker compose -f compose.observability.yaml ps grafana
```

Wait for `(healthy)`.

## Check that it works

**1. Log in.** Open http://127.0.0.1:3001. The username is `admin`; the password is in your secrets file:

```sh
cat observability/secrets/grafana_admin_password.txt; echo
```

**2. The data source is there and working.** Go to **Connections → Data sources**. **Prometheus** is listed, marked default, with a note that it was provisioned. Open it and click **Test** at the bottom: *Successfully queried the Prometheus API.* Try changing a field: Grafana won't let you save it, because Git owns this configuration.

You can check the same thing from the command line, which is useful in scripts:

```sh
GP=$(cat observability/secrets/grafana_admin_password.txt)
curl -s -u "admin:$GP" http://127.0.0.1:3001/api/datasources/uid/prometheus/health
```

```json
{"details":{"application":"Prometheus","features":{"rulerApiEnabled":false}},"message":"Successfully queried the Prometheus API.","status":"OK"}
```

**3. Explore the metrics from earlier parts.** Open **Explore** (the compass icon), make sure **Prometheus** is selected, switch the query editor to **Code**, and try:

```promql
sum by (service) (rate(http_requests_total[$__rate_interval]))
```

Requests per second per service, from Part 2. `$__rate_interval` is a Grafana variable that picks a safe range for `rate()` based on the time range and `timeInterval`. Prefer it over a hard-coded `[5m]` in Grafana.

```promql
histogram_quantile(0.95, sum by (service, le) (rate(http_request_duration_seconds_bucket[$__rate_interval])))
```

The 95th percentile latency per service: 95% of requests finished faster than this. Notice `sum by (service, le)`: the bucket boundary label `le` must survive the `sum`, otherwise `histogram_quantile` has no buckets to work with.

```promql
sum by (name) (container_memory_working_set_bytes{name!=""})
```

Memory per container, from Part 5. In the panel options on the right, set **Standard options → Unit** to *bytes (IEC)* and the numbers become readable.

**4. Prometheus sees Grafana.** In Prometheus, `up{job="grafana"}` is `1`.

## When something goes wrong

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Login fails with the secret's password | The volume already had an admin created with another password | Grafana sets the admin password only when its database is first created. Reset it: `docker compose -f compose.observability.yaml exec grafana grafana cli admin reset-admin-password "$(cat observability/secrets/grafana_admin_password.txt)"` |
| Data source test fails: `connection refused` | The URL uses `localhost` or `127.0.0.1` | Use the container name, `http://prometheus:9090`. |
| No provisioned data source | Wrong folder layout | The file must be under `provisioning/datasources/`. Check `docker compose -f compose.observability.yaml logs grafana` for `provisioning` errors. |
| Logs show `can't read alerting provisioning files` and `plugins` errors | Empty provisioning folders that don't exist yet | Harmless notices; Grafana is pointing out that it found nothing to provision there. |
| Port 3001 in use | Another program | Set `GRAFANA_PORT` to a free port. |

## What you have now

- Grafana `13.2.4` on http://127.0.0.1:3001, behind a password that never appears in a file you commit.
- The Prometheus data source defined in Git with a fixed UID.
- Prometheus monitoring Grafana.
- A place to explore every metric collected so far.

Metrics tell you *that* something is wrong. To find out *why*, you need logs. In [Part 7](07-store-logs-in-loki.md) we deploy Loki with a retention limit that's actually enforced.

## Key takeaways

- Choose Grafana for its ability to correlate metrics, logs and traces across different backends.
- Provision data sources (and later dashboards) from files in Git; UI-only setup can't be reproduced or reviewed.
- Set fixed data source UIDs so dashboards and cross-links never break.
- Use `__FILE` settings with Docker secrets for passwords. Never ship `admin`/`admin`.
- Grafana talks to backends by their Docker network names with `access: proxy`, so the backends stay private.
- Use `$__rate_interval` instead of fixed ranges in Grafana `rate()` queries.

## FAQ

### How do I run Grafana with Docker Compose?

Add a service using a pinned image such as `grafana/grafana:13.2.4`, publish port 3000 (on `127.0.0.1` if it's for local use), mount `/etc/grafana/provisioning` for data sources, and store Grafana's database in a named volume at `/var/lib/grafana`. Step 3 has a complete service definition.

### How do I provision a Prometheus data source in Grafana?

Create a YAML file in `/etc/grafana/provisioning/datasources/` with `apiVersion: 1` and a `datasources` list containing `name`, `uid`, `type: prometheus`, `access: proxy` and `url`. Grafana creates the data source on start-up and prevents it from being edited in the UI.

### How do I set the Grafana admin password from a Docker secret?

Mount the secret into the container and set `GF_SECURITY_ADMIN_PASSWORD__FILE=/run/secrets/<secret-name>`. The `__FILE` suffix works for any Grafana setting. Note that the password is applied only when Grafana's database is first created; use `grafana cli admin reset-admin-password` to change it afterwards.

### What is `$__rate_interval` in Grafana?

A variable Grafana replaces with a range suitable for `rate()` and `increase()`, based on the panel's time range, the number of data points and the data source's scrape interval. It prevents ranges that are too short to contain at least two samples, which would show gaps.

### Why can't I edit a provisioned data source in Grafana?

Provisioned resources belong to the files they came from, so Grafana blocks UI edits to stop the running instance from drifting away from the configuration in Git. Change the YAML file and restart Grafana instead.

---

**Series navigation:** Previous: [Part 5, Host and Container Metrics](05-host-and-container-metrics.md) · [Series index](README.md) · Next: [Part 7, Store Logs in Loki](07-store-logs-in-loki.md)
