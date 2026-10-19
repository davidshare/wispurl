---
title: "Observability for WispURL, Part 4: Monitor PostgreSQL, Redis and RabbitMQ"
seo_title: "Monitor PostgreSQL, Redis and RabbitMQ with Prometheus"
slug: monitor-postgres-redis-rabbitmq-prometheus
description: "Monitor PostgreSQL, Redis and RabbitMQ with Grafana Alloy's built-in exporters, a least-privilege pg_monitor user, Docker secrets and per-queue metrics."
series: "Observability for WispURL"
part: 4
date: 2026-10-17
last_updated: 2026-10-17
author: David Essien
tags: [postgresql, redis, rabbitmq, prometheus, grafana-alloy, exporters]
keywords:
  - "PostgreSQL Prometheus exporter"
  - "pg_monitor role"
  - "Redis exporter Prometheus"
  - "RabbitMQ Prometheus plugin"
  - "rabbitmq_prometheus detailed metrics"
  - "dead letter queue monitoring"
  - "Docker secrets Alloy"
difficulty: intermediate
estimated_time: 40 minutes
prerequisites:
  - "Part 3: Collect Service Metrics with Grafana Alloy"
repo_files:
  - db/init/create-monitoring-role.sh
  - docker-compose.yml
  - .env.example
  - compose.observability.yaml
  - observability/alloy/config.alloy
---

# Observability for WispURL, Part 4: Monitor PostgreSQL, Redis and RabbitMQ

> **In short:** use Grafana Alloy's built-in exporters for PostgreSQL and Redis instead of separate exporter containers, and RabbitMQ's own `rabbitmq_prometheus` plugin. Give the PostgreSQL exporter its own login with only the `pg_monitor` role and a connection limit, and pass its connection string as a Docker secret file (with no trailing newline). Scrape RabbitMQ's `/metrics/detailed` endpoint for per-queue depth, which you need to alert on a dead-letter queue.

The services can be perfectly healthy and still fail because something underneath them is struggling. WispURL depends on three pieces of infrastructure:

- **PostgreSQL** stores users, links and click statistics;
- **Redis** holds the rate limiter's counters;
- **RabbitMQ** carries click events to the analytics consumer and notifications to the notification worker.

In this part you will collect metrics from all three. You'll set up a read-only database user for monitoring, keep its password out of the Compose file, and make sure the dead-letter queue is visible.

## Design decisions

### Embedded exporters, not extra containers

Databases don't serve Prometheus metrics themselves. The classic answer is an **exporter**: a small program that queries the database and translates its statistics into Prometheus format. You'd normally run `postgres_exporter` and `redis_exporter` as two more containers.

Alloy has those same exporters **built in** (`prometheus.exporter.postgres` and `prometheus.exporter.redis` are the upstream projects compiled into Alloy). We use them because:

- there are two fewer containers to run, pin, upgrade and secure;
- configuration lives in one place, `config.alloy`;
- the metric names are identical to the standalone exporters, so community dashboards and alerts still apply.

The trade-off: the exporters share Alloy's lifecycle. Restart Alloy and database monitoring blinks for a few seconds. For a single host, that's fine.

RabbitMQ needs no exporter at all. Since version 3.8 it ships a plugin, `rabbitmq_prometheus`, that serves metrics directly. The plugin is maintained by the RabbitMQ team, so it's always in step with the broker.

### A dedicated, least-privilege database login

The quickest way to monitor PostgreSQL is to give the exporter the superuser password. Don't. The exporter's connection string sits in a file on disk and in the collector's memory; if either leaks, a superuser password means full control of every database.

PostgreSQL has a built-in role for exactly this job, **`pg_monitor`**. It grants read access to the statistics views (`pg_stat_activity`, `pg_stat_database`, `pg_settings` and others) and nothing else: it can't read your tables or change anything. We create a login, `wispurl_monitor`, with only that role, plus `CONNECTION LIMIT 3` so a misconfigured exporter can never use up the database's connections.

### Secrets as files, not environment variables

The connection string contains a password. Putting it in an environment variable would expose it to anyone who can run `docker inspect`, and it often ends up in logs and crash reports. Docker Compose **secrets** mount the value as a file at `/run/secrets/<name>` inside the container instead. Alloy reads the file. The file itself lives in `observability/secrets/`, which is git-ignored.

### Per-queue metrics for RabbitMQ, chosen carefully

RabbitMQ's plugin serves several endpoints:

| Endpoint | What it returns | Cost |
| --- | --- | --- |
| `/metrics` | Broker-wide totals: connections, memory, total messages | Cheap, constant size |
| `/metrics/per-object` | Everything for every queue, exchange and connection | Grows with every queue and connection; can be large |
| `/metrics/detailed?family=...` | Only the metric families you ask for, per object | You choose the cost |

We need to know how many messages sit in **each** queue, especially `events.dlq`, the dead-letter queue where events go after failing every retry. A message there means a click wasn't counted or a notification wasn't sent. The broker-wide totals can't tell you that.

So we scrape `/metrics` for the broker-wide view, plus `/metrics/detailed` with just two families: `queue_coarse_metrics` (messages ready, unacknowledged and total per queue) and `queue_consumer_count` (consumers per queue). That gives the per-queue numbers without paying for everything else.

## Step 1: Create the monitoring login

PostgreSQL's official image runs every script in `/docker-entrypoint-initdb.d/` the **first time** it initialises a data volume. WispURL already mounts `./db/init` there. Add a second script, `db/init/create-monitoring-role.sh`:

```bash
#!/usr/bin/env bash
# Creates a least-privilege login for the PostgreSQL metrics exporter (Alloy).
# pg_monitor grants read access to statistics views and nothing else.
#
# Postgres runs this automatically only when its data volume is first created.
# For an existing volume, run it once by hand:
#   docker compose exec postgres bash /docker-entrypoint-initdb.d/create-monitoring-role.sh
set -euo pipefail

: "${POSTGRES_MONITOR_PASSWORD:?POSTGRES_MONITOR_PASSWORD must be set (see .env.example)}"

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  --set monitor_password="$POSTGRES_MONITOR_PASSWORD" <<-'SQL'
  SELECT 'CREATE ROLE wispurl_monitor LOGIN'
  WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'wispurl_monitor')\gexec
  ALTER ROLE wispurl_monitor WITH LOGIN PASSWORD :'monitor_password' CONNECTION LIMIT 3;
  GRANT pg_monitor TO wispurl_monitor;
SQL
```

> `db/init/create-monitoring-role.sh` lines 1–20. Make it executable: `chmod +x db/init/create-monitoring-role.sh`.

How it works:

- **`: "${VAR:?message}"`** stops the script with a clear message if the password isn't set, rather than creating a login with an empty password.
- **It can run more than once.** PostgreSQL has no `CREATE ROLE IF NOT EXISTS`, so the `SELECT ... WHERE NOT EXISTS ... \gexec` line builds the `CREATE ROLE` statement only when the role is missing and then runs it. `ALTER ROLE` then sets the password every time, so re-running the script also resets the password.
- **The password never appears in SQL text.** `--set monitor_password=...` passes it as a psql variable, and `:'monitor_password'` inserts it as a properly quoted string. The heredoc delimiter is quoted (`<<-'SQL'`), so the shell doesn't expand anything inside it.
- **Init scripts run in alphabetical order.** `create-databases.sh` runs before `create-monitoring-role.sh`. Name scripts so the order is right.

Now pass the password to the Postgres container. In `docker-compose.yml`, add to the `postgres` service's `environment`:

```yaml
      # Password for the read-only wispurl_monitor role used by the metrics exporter.
      POSTGRES_MONITOR_PASSWORD: ${POSTGRES_MONITOR_PASSWORD:-}
```

> `docker-compose.yml` lines 58–59.

Document it in `.env.example`, so anyone setting up the project knows it exists:

```sh
# Read-only role for the PostgreSQL metrics exporter (db/init/create-monitoring-role.sh)
POSTGRES_MONITOR_PASSWORD=replace-with-a-long-random-monitor-password
```

And set a real value in your own `.env`:

```sh
printf '\nPOSTGRES_MONITOR_PASSWORD=%s\n' "$(openssl rand -hex 24)" >> .env
```

Hex output avoids characters such as `@`, `/` and `:` that would need escaping inside a connection URL.

### Apply it to your existing database

Init scripts only run on an **empty** data volume. Your database already exists, so recreate the container (to pick up the new variable) and run the script once:

```sh
docker compose up -d postgres
docker compose exec postgres bash /docker-entrypoint-initdb.d/create-monitoring-role.sh
```

You should see `CREATE ROLE`, `ALTER ROLE`, `GRANT ROLE`. Confirm the role has no superuser rights:

```sh
docker compose exec postgres psql -U postgres -c \
  "SELECT rolname, rolsuper, rolconnlimit FROM pg_roles WHERE rolname = 'wispurl_monitor';"
```

```text
     rolname     | rolsuper | rolconnlimit
-----------------+----------+--------------
 wispurl_monitor | f        |            3
```

## Step 2: Store the connection string as a secret

Build the connection string from your `.env` values and write it to the secrets folder:

```sh
mkdir -p observability/secrets
set -a; . ./.env; set +a
printf 'postgresql://wispurl_monitor:%s@postgres:5432/%s?sslmode=disable' \
  "$POSTGRES_MONITOR_PASSWORD" "$POSTGRES_DB" > observability/secrets/postgres_dsn.txt
chmod 600 observability/secrets/postgres_dsn.txt
```

Three details matter here:

- **No trailing newline.** `printf` without `\n` at the end writes the string exactly. `echo` would add a newline, and the exporter rejects a connection string ending in a newline: Alloy fails to load its config and restarts in a loop. This is an easy mistake that's hard to spot, because the file looks fine in an editor.
- **`sslmode=disable`** is acceptable because the connection never leaves the Docker network on your machine. Across a real network, use `sslmode=verify-full` with the server's CA certificate.
- **`chmod 600`** means only your user can read the file.

Check it's git-ignored:

```sh
git check-ignore observability/secrets/postgres_dsn.txt && echo ignored
```

Now declare the secret in `compose.observability.yaml`. At the bottom of the file:

```yaml
secrets:
  postgres_dsn:
    file: ./observability/secrets/postgres_dsn.txt
```

> `compose.observability.yaml` lines 229–231.

And give it to Alloy, in the `alloy` service:

```yaml
    secrets:
      - postgres_dsn
```

> `compose.observability.yaml` lines 113–114.

Inside the Alloy container the file appears at `/run/secrets/postgres_dsn`.

## Step 3: Add the exporters to Alloy

Append these sections to `observability/alloy/config.alloy`.

### Redis

```alloy
prometheus.exporter.redis "redis" {
  redis_addr = "redis:6379"
}

prometheus.scrape "redis" {
  targets         = prometheus.exporter.redis.redis.targets
  job_name        = "redis"
  scrape_interval = "15s"
  scrape_timeout  = "10s"
  forward_to      = [prometheus.remote_write.prometheus.receiver]
}
```

> `config.alloy` lines 330–340.

This is the pattern every embedded exporter follows: a `prometheus.exporter.*` component that **exports targets**, and a `prometheus.scrape` that scrapes those targets and forwards the results, exactly like the service metrics in Part 3. The exporter doesn't send anything on its own.

The local Redis has no password, so only the address is needed. If yours has one, add `redis_password_file` pointing at another Docker secret.

> **About the `job` label.** Embedded exporters label their own targets `job="integrations/<exporter>"`, and `prometheus.scrape` only applies `job_name` to targets that don't already have a `job` label. So Redis metrics arrive as `job="integrations/redis"` and PostgreSQL as `job="integrations/postgres"`, not `redis` and `postgres`. Keep that in mind when writing queries and alerts, or query by metric name (`redis_up`, `pg_up`), which is what this series does. The RabbitMQ targets below are written by hand without a `job` label, so they do get `job_name`.

### RabbitMQ

First, the broker must have the plugin enabled. WispURL's `rabbitmq` service in `docker-compose.yml` enables it before starting the server:

```yaml
    command:
      - sh
      - -c
      - |
        rabbitmq-plugins enable --offline rabbitmq_prometheus &&
        rabbitmq-server
```

> `docker-compose.yml` lines 626–631.

`--offline` enables the plugin without a running broker, so it's active from the very first start. The plugin listens on port **15692**.

Then scrape both endpoints:

```alloy
prometheus.scrape "rabbitmq" {
  targets = [
    {
      "__address__" = "rabbitmq:15692",
      "instance"    = "rabbitmq",
      "environment" = "docker",
      "application" = "wispurl",
    },
  ]

  job_name        = "rabbitmq"
  metrics_path    = "/metrics"
  scrape_interval = "15s"
  scrape_timeout  = "10s"
  forward_to      = [prometheus.remote_write.prometheus.receiver]
}

// /metrics above only has broker-wide totals. Per-queue depth and consumer
// counts (needed to alert on the dead-letter queue) live on /metrics/detailed.
prometheus.scrape "rabbitmq_queues" {
  targets = [
    {
      "__address__" = "rabbitmq:15692",
      "instance"    = "rabbitmq",
      "environment" = "docker",
      "application" = "wispurl",
    },
  ]

  job_name        = "rabbitmq-queues"
  metrics_path    = "/metrics/detailed"
  params          = {
    "family" = ["queue_coarse_metrics", "queue_consumer_count"],
  }
  scrape_interval = "15s"
  scrape_timeout  = "10s"
  forward_to      = [prometheus.remote_write.prometheus.receiver]
}
```

> `config.alloy` lines 349–386.

- These targets are **static**: there's one broker at a fixed name, so discovery would add nothing. Setting `instance = "rabbitmq"` replaces the default `rabbitmq:15692`, which reads better on dashboards.
- **`params`** adds query-string parameters. `family` appears twice, so the scrape URL becomes `/metrics/detailed?family=queue_coarse_metrics&family=queue_consumer_count`.
- Two separate jobs keep the two kinds of data apart: `job="rabbitmq"` for the broker and `job="rabbitmq-queues"` for queues.

### PostgreSQL

```alloy
local.file "postgres_dsn" {
  filename  = "/run/secrets/postgres_dsn"
  is_secret = true
}

prometheus.exporter.postgres "postgres" {
  data_source_names = [local.file.postgres_dsn.content]
}

prometheus.scrape "postgres" {
  targets         = prometheus.exporter.postgres.postgres.targets
  job_name        = "postgres"
  scrape_interval = "15s"
  scrape_timeout  = "10s"
  forward_to      = [prometheus.remote_write.prometheus.receiver]
}
```

> `config.alloy` lines 398–413.

- **`local.file`** reads a file and exports its contents. It also watches the file: rotate the password, rewrite the file, and Alloy picks up the new value without a restart.
- **`is_secret = true`** marks the contents as sensitive, so Alloy hides the value in its UI and debug output.
- One exporter connection covers every database on the server. `pg_stat_database` and `pg_database_size_bytes` report per database (`auth_db`, `short_db`, `stats_db`) without separate connections to each.

Validate and restart Alloy:

```sh
docker run --rm -e WISPURL_NETWORK=wispurl_wispurl-network \
  -v "$PWD/observability/alloy:/c:ro" grafana/alloy:v1.20.1 validate /c/config.alloy && echo valid
docker compose -f compose.observability.yaml up -d alloy
```

`up -d` recreates Alloy here because its Compose definition changed (the new secret). For config-only changes later, use `restart alloy`.

## What to watch for each dependency

Collecting hundreds of metrics is easy; knowing which few matter is the real work. These are the ones worth a dashboard panel or an alert, and why.

| Dependency | Question | PromQL |
| --- | --- | --- |
| PostgreSQL | Is it reachable? | `pg_up` |
| | Are we close to running out of connections? | `sum(pg_stat_activity_count) / max(pg_settings_max_connections)` |
| | How fast are the databases growing? | `pg_database_size_bytes{datname=~"auth_db\|short_db\|stats_db"}` |
| | Throughput and contention | `rate(pg_stat_database_xact_commit[5m])`, `rate(pg_stat_database_deadlocks[5m])` |
| Redis | Is it reachable? | `redis_up` |
| | How many clients, how much memory? | `redis_connected_clients`, `redis_memory_used_bytes` |
| | How busy is it? | `rate(redis_commands_processed_total[5m])` |
| RabbitMQ | Is anything stuck in the dead-letter queue? | `rabbitmq_detailed_queue_messages{queue="events.dlq"}` |
| | Are consumers keeping up? | `rabbitmq_detailed_queue_messages_ready` per queue |
| | Is every queue being consumed? | `rabbitmq_detailed_queue_consumers` (0 means nothing is reading) |
| | Is the broker under resource pressure? | `rabbitmq_process_resident_memory_bytes`, `rabbitmq_disk_space_available_bytes` |

The connection ratio deserves a word. WispURL's Postgres allows 200 connections, and each service keeps a bounded pool. If the ratio climbs towards 1, new requests will soon get "too many connections" errors. That's why it becomes an alert in Part 15, at 80%.

## Check that it works

In Prometheus (http://127.0.0.1:9090):

```promql
pg_up
```

returns `1`. If it returns `0`, the exporter is running but can't log in. Check the role and the connection string.

```promql
count by (datname) (pg_stat_activity_count)
```

lists every database, including `auth_db`, `short_db` and `stats_db`, all from one connection.

```promql
redis_up
```

returns `1`.

```promql
rabbitmq_detailed_queue_messages
```

returns one series per queue:

```text
rabbitmq_detailed_queue_messages{instance="rabbitmq", job="rabbitmq-queues", queue="analytics.clicks", vhost="/"}  0
rabbitmq_detailed_queue_messages{instance="rabbitmq", job="rabbitmq-queues", queue="events.dlq", vhost="/"}  0
rabbitmq_detailed_queue_messages{instance="rabbitmq", job="rabbitmq-queues", queue="notifications.all", vhost="/"}  0
```

`events.dlq` at `0` is what you want to see.

**Prove the exporter really is read-only.** Try to read application data as the monitoring user:

```sh
docker compose exec postgres sh -c \
  'PGPASSWORD="$POSTGRES_MONITOR_PASSWORD" psql -h localhost -U wispurl_monitor -d short_db -c "SELECT count(*) FROM links;"'
```

```text
ERROR:  permission denied for table links
```

The single quotes make the container's shell, which has `POSTGRES_MONITOR_PASSWORD` set, expand the variable, so the password never appears on your command line. Swap the query for `SELECT count(*) FROM pg_stat_activity;` and it works: the exporter can see statistics, but not your users' data.

## When something goes wrong

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Alloy restarts in a loop; logs say `cannot parse DSN ... invalid control character` | The DSN file ends with a newline | Recreate it with `printf` and no `\n`. Check with `tail -c1 observability/secrets/postgres_dsn.txt \| od -c`. |
| `pg_up` is `0` | Wrong password or missing role | Re-run the role script; rebuild the DSN from `.env`. |
| `password authentication failed for user "wispurl_monitor"` | `.env` and the database disagree | Re-running the script resets the password to the current `.env` value. |
| No `rabbitmq_*` metrics | Plugin not enabled | Check the `rabbitmq` service's `command`; `docker compose exec rabbitmq rabbitmq-plugins list` should mark `rabbitmq_prometheus` as enabled. |
| No `rabbitmq_detailed_*` metrics | Missing `params` | The `family` parameter must be set; without it `/metrics/detailed` returns nothing. |
| The role script fails with `POSTGRES_MONITOR_PASSWORD must be set` | The variable didn't reach the container | Add it to `.env` and the `postgres` environment, then `docker compose up -d postgres` before running the script. |

## What you have now

- PostgreSQL, Redis and RabbitMQ metrics in Prometheus, with no extra exporter containers.
- A monitoring login that can read statistics and nothing else, limited to three connections.
- Its password stored as a git-ignored Docker secret, reloaded automatically when it changes.
- Per-queue RabbitMQ metrics, including the dead-letter queue.

In [Part 5](05-host-and-container-metrics.md) we add the layer underneath everything: CPU, memory and disk for the Docker host and for each container.

## Key takeaways

- Prefer embedded exporters in your collector when you run a single host; the metric names match the standalone exporters.
- Never monitor a database as a superuser. PostgreSQL's `pg_monitor` role exists exactly for exporters.
- Pass credentials as Docker secret files, not environment variables, and write them without a trailing newline.
- Init scripts in `/docker-entrypoint-initdb.d` only run on an empty volume. Make them safe to re-run, and run them by hand for existing databases.
- Broker-wide RabbitMQ totals hide stuck queues. Scrape per-queue metrics, but only the families you need.
- Pick a handful of metrics per dependency that answer real questions; those become dashboards and alerts.

## FAQ

### How do I monitor PostgreSQL with Prometheus?

Run a PostgreSQL exporter, either the standalone `postgres_exporter` or the one built into Grafana Alloy (`prometheus.exporter.postgres`), and scrape it. Give it a dedicated login with only the `pg_monitor` role. Key metrics are `pg_up`, `pg_stat_activity_count` against `pg_settings_max_connections`, and `pg_database_size_bytes`.

### What permissions does a PostgreSQL monitoring user need?

Grant the built-in `pg_monitor` role. It allows reading statistics views such as `pg_stat_activity`, `pg_stat_database` and `pg_settings`, without access to application tables. Add a connection limit (for example `CONNECTION LIMIT 3`) so the exporter can't exhaust the database's connections.

### How do I get RabbitMQ queue metrics in Prometheus?

Enable the `rabbitmq_prometheus` plugin and scrape port 15692. The default `/metrics` endpoint returns broker-wide totals. For per-queue numbers, scrape `/metrics/detailed` with `family=queue_coarse_metrics` (messages per queue) and `family=queue_consumer_count`, or use `/metrics/per-object` if you need everything.

### How do I monitor a RabbitMQ dead-letter queue?

Collect per-queue metrics as above and watch `rabbitmq_detailed_queue_messages{queue="<your dlq>"}`. Any value above zero means messages failed processing after all retries. Part 15 turns this into an alert.

### Why does Grafana Alloy fail to parse my PostgreSQL DSN?

The most common cause is a trailing newline in the DSN file, which happens when it's written with `echo` or saved by an editor. Write it with `printf '%s'` and no `\n`, and check the last byte with `tail -c1 file | od -c`.

---

**Series navigation:** Previous: [Part 3, Collect Service Metrics with Grafana Alloy](03-collect-service-metrics-with-alloy.md) · [Series index](README.md) · Next: [Part 5, Host and Container Metrics](05-host-and-container-metrics.md)
