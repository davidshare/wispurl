---
title: "Observability for WispURL, Part 14: Dashboards as Code"
seo_title: "Grafana Dashboards as Code: RED and USE Dashboards in Git"
slug: grafana-dashboards-as-code-red-use
description: "Build RED and USE Grafana dashboards, provision them from JSON files in Git, and learn a practical workflow for changing provisioned dashboards safely."
series: "Observability for WispURL"
part: 14
date: 2026-10-17
last_updated: 2026-10-17
author: David Essien
tags: [grafana, dashboards, provisioning, promql, red-method, use-method]
keywords:
  - "Grafana dashboards as code"
  - "Grafana dashboard provisioning"
  - "RED dashboard Grafana"
  - "USE method dashboard"
  - "Grafana dashboard JSON model"
  - "Grafana template variables"
  - "PromQL dashboard queries"
difficulty: intermediate
estimated_time: 40 minutes
prerequisites:
  - "Part 13: Link Logs and Traces"
repo_files:
  - observability/grafana/provisioning/dashboards/dashboards.yaml
  - observability/grafana/dashboards/wispurl-red.json
  - observability/grafana/dashboards/wispurl-use.json
---

# Observability for WispURL, Part 14: Dashboards as Code

> **In short:** keep two focused dashboards in Git, a **RED** dashboard for services (requests per second, 5xx ratio, p50/p95/p99 latency, in-progress requests, error logs) and a **USE** dashboard for resources (host CPU, memory, disk and load, per-container CPU and memory, Postgres connections, RabbitMQ queues, Redis). Load them with a Grafana dashboard provider that reads JSON files, blocks UI edits (`allowUiUpdates: false`) and keeps fixed UIDs. To change one, copy it in the UI, edit, export the JSON, and commit the file.

You've been exploring with ad-hoc queries since Part 6. During an incident nobody wants to type PromQL from memory. In this part you'll build two dashboards that answer the first questions anyone asks, "is something wrong, and where?", and keep them in Git like the rest of the configuration.

## Design decisions

### A few dashboards, each answering one question

Dashboards multiply. Teams end up with dozens, half of them broken, none trusted. We keep two, each with a clear purpose:

| Dashboard | Question it answers | Method |
| --- | --- | --- |
| **WispURL — Services (RED)** | Are users affected? Which service? | RED: rate, errors, duration |
| **WispURL — Resources (USE)** | Is something underneath running out? | USE: utilization, saturation, errors |

The order you look at them follows the investigation: RED first (are users affected?), then USE (is a resource the cause?), then a trace or a log line for the details (Parts 11–13).

### Lay out from top to bottom by importance

Within each dashboard, rows go from the most important signal to the most detailed: rate, then errors, then duration, then logs. Someone glancing at the top half should already know whether there's a problem. Every panel has a unit (requests per second, percent, seconds, bytes), so nobody has to guess what a number means, and a description where the meaning isn't obvious.

### JSON files, not code generators

Dashboards can be written by hand in the UI, or generated from code with **Grafonnet** (Jsonnet), the **Grafana Foundation SDK** (Go, TypeScript, Python) or the **Terraform Grafana provider**. Generators pay off when you have many similar dashboards: one change updates them all.

For two dashboards, plain JSON exported from Grafana is the simplest thing that works: anyone can open it, there's no build step, and the UI remains the editor. Switch to a generator when you find yourself copying the same panel between several dashboards.

### Git is the source of truth; the UI can't override it

As with data sources (Part 6), dashboards are **provisioned** from files. The provider is set so the UI can't save changes to them. That sounds restrictive, but it prevents the most common dashboard problem: someone "quickly fixes" a panel in production, and the fix is lost or silently diverges from what's in Git. The editing workflow below shows how to make changes properly.

## Step 1: The dashboard provider

Create `observability/grafana/provisioning/dashboards/dashboards.yaml`:

```yaml
apiVersion: 1

# Load every dashboard JSON file in /var/lib/grafana/dashboards into a
# "WispURL" folder. Dashboards live in Git; edits made in the UI are refused so
# the files stay the source of truth.
providers:
  - name: wispurl
    folder: WispURL
    type: file
    disableDeletion: true
    allowUiUpdates: false
    updateIntervalSeconds: 30
    options:
      path: /var/lib/grafana/dashboards
```

> `dashboards.yaml` lines 1–14.

| Setting | Effect |
| --- | --- |
| `folder: WispURL` | Dashboards appear in a **WispURL** folder |
| `type: file` | Read dashboards from files |
| `options.path` | The folder Part 6 mounted read-only from `observability/grafana/dashboards` |
| `disableDeletion: true` | Dashboards can't be deleted from the UI |
| `allowUiUpdates: false` | Changes can't be saved from the UI |
| `updateIntervalSeconds: 30` | Grafana checks the folder every 30 seconds, so a changed file goes live without a restart |

## Step 2: The anatomy of a dashboard file

A dashboard is a JSON document. The parts that matter:

```json
{
  "uid": "wispurl-red",
  "title": "WispURL — Services (RED)",
  "editable": false,
  "schemaVersion": 41,
  "time": { "from": "now-1h", "to": "now" },
  "refresh": "30s",
  "templating": { "list": [ ... variables ... ] },
  "panels": [ ... ]
}
```

> `observability/grafana/dashboards/wispurl-red.json` lines 1–14 (shown condensed).

- **`uid`**: a fixed, readable ID. The dashboard's URL is built from it (`/d/wispurl-red/...`), so links in runbooks and alerts (Parts 15 and 16) keep working. Without a fixed UID, Grafana generates one, and every link breaks when the dashboard is re-imported.
- **`schemaVersion`**: the JSON format version. Grafana upgrades older dashboards automatically when it loads them.
- **`refresh: "30s"`** with **`time: now-1h`**: shows the last hour and refreshes every 30 seconds. Refreshing more often than the 15-second scrape interval just repeats the same data.

A panel looks like this:

```json
{
  "id": 5,
  "type": "timeseries",
  "title": "5xx error ratio",
  "description": "Share of requests answered with a 5xx. HighErrorRate fires above 5%.",
  "datasource": { "type": "prometheus", "uid": "prometheus" },
  "gridPos": { "x": 0, "y": 10, "w": 12, "h": 8 },
  "fieldConfig": { "defaults": { "unit": "percentunit" }, "overrides": [] },
  "targets": [
    {
      "refId": "A",
      "datasource": { "type": "prometheus", "uid": "prometheus" },
      "expr": "sum by (service) (rate(http_requests_total{service=~\"$service\",status=~\"5..\"}[$__rate_interval])) / sum by (service) (rate(http_requests_total{service=~\"$service\"}[$__rate_interval]))",
      "legendFormat": "{{service}}"
    }
  ]
}
```

> `wispurl-red.json` lines 152–193 (condensed).

- **`datasource.uid`** refers to the data source by the fixed UID from Part 6. Exported dashboards that refer to data sources by name, or by an auto-generated UID, break on another Grafana instance.
- **`gridPos`**: the dashboard is a grid **24 columns wide**. `w: 12` is half the width; `h: 8` is the height in rows; `x` and `y` place the panel.
- **`fieldConfig.defaults.unit`**: `percentunit` displays `0.05` as `5%`. Other units used here: `reqps`, `s`, `bytes`, `short`.
- **`description`** shows as an ⓘ tooltip. Linking a panel to the alert that watches it helps people connect the two.
- **`legendFormat: "{{service}}"`** names each line after its `service` label instead of the full series name.

## Step 3: The RED dashboard

`observability/grafana/dashboards/wispurl-red.json` has one variable and four rows.

### A `service` variable

```json
{
  "name": "service",
  "label": "Service",
  "type": "query",
  "datasource": { "type": "prometheus", "uid": "prometheus" },
  "query": { "query": "label_values(http_requests_total, service)", "refId": "service" },
  "includeAll": true,
  "multi": true,
  "current": { "text": "All", "value": "$__all" },
  "refresh": 2
}
```

> `wispurl-red.json` lines 17–38 (condensed).

This creates a **Service** drop-down at the top of the dashboard, filled with every value of the `service` label. Every query filters with `service=~"$service"`, so choosing `shortener-service` narrows every panel at once. `multi` allows several services, `includeAll` adds "All", and `refresh: 2` refreshes the list whenever the time range changes, so new services appear by themselves.

The **Error logs** panel uses the same variable against Loki (`{service=~"$service", level=~"error|critical"}`). That only works because metrics and logs use the same service names (Part 2).

### The panels

| Row | Panel | PromQL (with `$service` filter omitted for readability) | Unit |
| --- | --- | --- | --- |
| Rate | Requests per second | `sum by (service) (rate(http_requests_total[$__rate_interval]))` | req/s |
| | Busiest routes | `topk(10, sum by (service, path) (rate(http_requests_total[$__rate_interval])))` | req/s |
| Errors | 5xx error ratio | `sum by (service) (rate(http_requests_total{status=~"5.."}[$__rate_interval])) / sum by (service) (rate(http_requests_total[$__rate_interval]))` | % |
| | Responses by status | `sum by (status) (rate(http_requests_total[$__rate_interval]))` | req/s |
| Duration | Latency p50 / p95 / p99 | `histogram_quantile(0.95, sum by (service, le) (rate(http_request_duration_seconds_bucket[$__rate_interval])))` (and 0.50, 0.99) | s |
| | Requests in progress | `sum by (service) (http_requests_in_progress)` | count |
| Logs | Error logs | Loki: `{service=~"$service", level=~"error\|critical"}` | — |

Notes on the queries:

- **Ratios, not counts, for errors.** "12 errors per second" means nothing without the total. The ratio (errors divided by all requests) is what users feel, and it's what the alert in Part 15 uses.
- **The 5xx panel may show "No data".** If nothing has failed, `status=~"5.."` matches no series, and Grafana shows no data instead of 0. That's correct, and it's good news.
- **Three percentiles, not an average.** An average hides the slow requests users complain about. p50 shows the typical request, p95 and p99 the slow tail. A widening gap between p50 and p99 is often the first sign of trouble.
- **`sum by (service, le)`** keeps the bucket label `le` so `histogram_quantile` can work, as explained in Part 6.
- **`topk(10, ...)`** keeps the busiest routes panel readable as traffic grows. Route templates (Part 2) keep it meaningful: `/{short_code}` is one line, not a line per link.

## Step 4: The USE dashboard

`observability/grafana/dashboards/wispurl-use.json` has three rows and no variables. The queries are the ones explained in Parts 4 and 5:

| Row | Panel | PromQL | Unit |
| --- | --- | --- | --- |
| Docker host | CPU utilization | `1 - avg(rate(node_cpu_seconds_total{mode="idle"}[$__rate_interval]))` | % |
| | Memory utilization | `1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes` | % |
| | Docker data disk used | `1 - min(node_filesystem_avail_bytes{mountpoint=~"/\|/var/lib/docker", ...} / node_filesystem_size_bytes{...})` | % |
| | Load average (saturation) | `node_load1`, `node_load5`, and `count(node_cpu_seconds_total{mode="idle"})` as a reference line | count |
| | Network errors | `sum(rate(node_network_receive_errs_total[...]) + rate(node_network_transmit_errs_total[...]))` | /s |
| Containers | CPU by container | `sum by (name) (rate(container_cpu_usage_seconds_total{name!=""}[$__rate_interval]))` | cores |
| | Memory by container | `sum by (name) (container_memory_working_set_bytes{name!=""})` | bytes |
| Dependencies | PostgreSQL connections used | `sum(pg_stat_activity_count) / max(pg_settings_max_connections)` | % |
| | RabbitMQ messages per queue | `sum by (queue) (rabbitmq_detailed_queue_messages)` | count |
| | Redis memory and clients | `redis_memory_used_bytes`, `redis_connected_clients` | — |

The load panel shows the CPU count as a third line on purpose: load only means something next to the number of CPUs. When `node_load1` crosses the CPU-count line, work is queuing.

## Step 5: Load them

The dashboards folder is already mounted (Part 6). Put the two JSON files in `observability/grafana/dashboards/` and the provider file in `provisioning/dashboards/`, then restart Grafana once so it reads the new provider:

```sh
docker compose -f compose.observability.yaml restart grafana
```

After that, changed dashboard files are picked up within 30 seconds without a restart.

## How to change a provisioned dashboard

Because the UI can't save provisioned dashboards, use this workflow:

1. Open the dashboard and click **Edit**, then use **Save as** to save a copy in a different folder, for example *Scratch*. A copy isn't provisioned, so you can edit it freely.
2. Make your changes in the copy: add panels, adjust queries, rearrange.
3. Export it: **Export → Export as JSON**. Leave **Export the dashboard to use in another instance** *off*, so data sources are kept as the fixed UIDs (`prometheus`, `loki`) instead of being replaced with placeholders.
4. In the exported JSON, set `uid` and `title` back to the original's (`wispurl-red`, `WispURL — Services (RED)`).
5. Replace the file in `observability/grafana/dashboards/`, review the diff, and commit.
6. Within 30 seconds Grafana reloads it. Delete the scratch copy.

For small changes, such as a query or a unit, editing the JSON directly is often quicker. Grafana validates it when loading; check `docker compose -f compose.observability.yaml logs grafana` if the dashboard doesn't update.

## Check that it works

Open http://127.0.0.1:3001 → **Dashboards** → **WispURL**. Both dashboards are listed.

**RED dashboard.** Generate some traffic: click around the app, or run a loop:

```sh
for i in $(seq 1 200); do curl -s -o /dev/null http://localhost:8080/<short-code>; done
```

The **Requests per second** panel rises for `gateway` and `shortener-service`; **Busiest routes** shows `/{short_code}` at the top; **Latency** shows the p50/p95/p99 spread. Switch the **Service** drop-down to `auth-service` and every panel narrows to it, including the error logs.

**USE dashboard.** Containers sorted by memory, host CPU and load against the CPU count, `events.dlq` at 0 in the RabbitMQ panel.

**Verify that every panel's query is valid.** It's worth automating: run each query from the JSON against Prometheus's API and flag any that return an error or nothing at all. An empty 5xx panel is expected; an empty CPU panel is a bug.

**Confirm the protection.** Try to save a change to a provisioned dashboard: Grafana refuses, saying it was provisioned and can't be saved.

## When something goes wrong

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Dashboards don't appear | Provider file in the wrong place, or Grafana not restarted after adding it | It must be in `provisioning/dashboards/`; restart Grafana once. |
| "Datasource not found" on every panel | The JSON refers to data sources by another UID or name | Use `"uid": "prometheus"` / `"loki"` and export with external sharing off. |
| Panel says "No data" | The query matches nothing | Run it in Explore; check label names (`service`, not `job`, for app metrics). |
| The Service drop-down is empty | No `http_requests_total` yet, or the variable query is wrong | Generate traffic; check `label_values(http_requests_total, service)`. |
| A change to the JSON doesn't show up | Invalid JSON, or a `uid` clash with another file | Check Grafana's logs; every dashboard needs a unique `uid`. |
| Saving in the UI fails | Expected: `allowUiUpdates: false` | Use the editing workflow above. |

## What you have now

- A RED dashboard showing user impact per service, with drill-down by service and error logs alongside.
- A USE dashboard showing whether the host, containers or dependencies are under pressure.
- Both in Git, loaded automatically, protected from accidental edits, and reachable by stable URLs.

Dashboards help when someone is looking. In [Part 15](15-alerting-with-alertmanager.md) we make the system tell you when something is wrong, with alert rules, routing and local email delivery.

## Key takeaways

- Keep a small number of dashboards, each answering one question: RED for user impact, USE for resources.
- Order panels by importance, give every panel a unit, and describe non-obvious ones.
- Provision dashboards from files with fixed UIDs; block UI edits so Git stays the source of truth.
- Show error ratios and percentiles, not raw error counts or averages.
- Template variables like `$service` make one dashboard serve every service, provided labels are consistent.
- Change provisioned dashboards by copying, editing, exporting and committing.

## FAQ

### How do I provision Grafana dashboards from files?

Add a provider file in `/etc/grafana/provisioning/dashboards/` with `type: file` and `options.path` pointing at a folder of dashboard JSON files, and mount that folder into the container. Grafana loads every JSON file it finds and reloads changed files every `updateIntervalSeconds`.

### What should a RED dashboard include?

Request rate per service, error ratio (5xx divided by all requests), and latency percentiles (p50, p95, p99) from a histogram, ideally with a service filter. Adding in-progress requests (saturation) and a panel of error logs makes it a complete first stop during an incident.

### What is the USE method for dashboards?

For each resource (CPU, memory, disk, network, connection pools, queues), show Utilization (how busy), Saturation (work waiting) and Errors. On a host that means CPU usage and load against CPU count, available memory, disk space, and network errors; for dependencies, connection usage and queue depth.

### How do I edit a provisioned Grafana dashboard?

Save a copy to a non-provisioned folder, edit the copy, export it as JSON with external sharing off, restore the original `uid` and `title`, replace the file in your repository, and commit. Grafana reloads it automatically.

### Should I use Grafonnet or Terraform for Grafana dashboards?

Use a generator such as Grafonnet, the Grafana Foundation SDK or Terraform when you maintain many dashboards with repeated panels, so one change updates them all. For a handful of dashboards, JSON files exported from Grafana and kept in Git are simpler.

---

**Series navigation:** Previous: [Part 13, Link Logs and Traces](13-link-logs-and-traces.md) · [Series index](README.md) · Next: [Part 15, Alerting with Prometheus and Alertmanager](15-alerting-with-alertmanager.md)
