---
title: "Observability for WispURL, Part 5: Host and Container Metrics"
seo_title: "Docker Host and Container Metrics with Alloy and cAdvisor"
slug: docker-host-container-metrics-alloy-cadvisor
description: "Collect CPU, memory, disk and network metrics for the Docker host and every container with Grafana Alloy's node and cAdvisor exporters, the USE method way."
series: "Observability for WispURL"
part: 5
date: 2026-10-17
last_updated: 2026-10-17
author: David Essien
tags: [cadvisor, node-exporter, docker, grafana-alloy, use-method, prometheus]
keywords:
  - "cAdvisor Docker Compose"
  - "node exporter Docker"
  - "Grafana Alloy cadvisor"
  - "container CPU memory metrics Prometheus"
  - "USE method monitoring"
  - "Docker Desktop cAdvisor"
  - "cgroup host namespace"
difficulty: intermediate
estimated_time: 35 minutes
prerequisites:
  - "Part 4: Monitor PostgreSQL, Redis and RabbitMQ"
repo_files:
  - compose.observability.yaml
  - observability/alloy/config.alloy
---

# Observability for WispURL, Part 5: Host and Container Metrics

> **In short:** add Grafana Alloy's built-in node exporter (`prometheus.exporter.unix`) for host CPU, memory, disk and network, and its built-in cAdvisor (`prometheus.exporter.cadvisor`) for per-container usage. The node exporter needs the host's `/proc`, `/sys` and `/` mounted read-only. cAdvisor needs the Docker and containerd sockets plus `cgroup: host`, otherwise it can only see Alloy's own container. Give both a fixed `instance` label so recreating Alloy doesn't start new series. On Docker Desktop, all of this describes Docker's Linux VM, not your Mac or Windows machine.

So far we measure what users experience (Part 2) and what our dependencies are doing (Part 4). Underneath both sits the machine itself. If the disk fills or memory runs out, everything above fails at once, usually with confusing symptoms.

In this part you'll collect:

- **host metrics**: CPU, memory, disk and network for the machine running Docker;
- **container metrics**: CPU, memory and network for every container.

## The USE method

In Part 2 we used RED (rate, errors, duration) for services. For **resources** (CPUs, memory, disks, network links) the matching method is **USE**, from performance engineer Brendan Gregg:

| Letter | Meaning | CPU example | Disk example |
| --- | --- | --- | --- |
| **U**tilization | How busy the resource is | 60% of CPU time in use | 85% of space used |
| **S**aturation | Work waiting because the resource is busy | Load average above the CPU count | I/O requests queuing |
| **E**rrors | Things failing | — | Read or write errors |

For every resource, ask all three. A CPU at 100% with nothing waiting is busy but coping. A CPU at 70% with a long run queue is already slowing requests down. Saturation is the signal people most often forget, and the one that predicts trouble.

## Design decisions

### Built into Alloy again

The usual approach is two more containers: `node_exporter` for the host and `cadvisor` for containers. As in Part 4, Alloy embeds both, so we use them for the same reasons: fewer containers, one config, the same metric names as the standalone tools.

### What "host" means on Docker Desktop

On Linux, Docker runs directly on your machine, so host metrics describe your machine. On macOS and Windows, **Docker Desktop runs a Linux virtual machine** and every container runs inside it. A container can only see that VM, so "host" metrics describe the VM: its CPU count, its memory allocation and its virtual disk.

That's actually what you want for capacity planning: the VM's limits are the limits your containers live within. Just don't expect the numbers to match your laptop's Activity Monitor.

### Giving a container a view of the host, and what that costs

A container normally sees its own isolated view of processes, filesystems and resource usage. To report on the whole host, the exporters need to look outside that box:

| Mount or setting | Why |
| --- | --- |
| `/proc:/host/proc:ro` | Host CPU, memory, load and network counters live in `/proc` |
| `/sys:/host/sys:ro` | Hardware and filesystem details |
| `/:/host/root:ro` | Lets the exporter measure the host's filesystems |
| `/run/containerd/containerd.sock` | cAdvisor looks up container details through containerd |
| `cgroup: host` | Lets cAdvisor see every container's resource accounting |

These are mounted read-only, but read-only access to the host's root filesystem still exposes every file on it, including other containers' data. Together with the Docker socket from Part 3 (and the containerd socket, which carries the same risk), **Alloy now has very broad access to the host**. That's normal for a node-level monitoring agent, and it's why such agents should run as trusted, pinned, minimal images with read-only configuration. On a shared server, consider running these exporters as separate, tightly scoped containers instead of in your main collector.

### Why `cgroup: host`

Linux tracks each container's CPU and memory in **cgroups**. Docker gives every container its own cgroup **namespace**, so a container looking at `/sys/fs/cgroup` sees only its own usage. cAdvisor running inside Alloy would report exactly one "container": Alloy itself.

`cgroup: host` tells Docker to share the host's cgroup namespace with Alloy, so cAdvisor can see every container's accounting. Without it you get no per-container metrics and no error: the exporter simply finds nothing to report.

### A fixed `instance` label

Embedded exporters set `instance` to Alloy's own hostname, which is the container ID and changes every time Alloy is recreated. Each recreation would start a fresh set of series, and graphs would show several overlapping lines for one machine. We overwrite `instance` with a fixed value, `docker-host`.

## Step 1: Give Alloy a view of the host

Add these to the `alloy` service in `compose.observability.yaml`, below the Docker socket mount:

```yaml
      # cAdvisor reads container details from containerd (same caveat as above).
      - /run/containerd/containerd.sock:/run/containerd/containerd.sock:ro
      # Host views for the node exporter (CPU, memory, disk, network).
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/host/root:ro
    # Share the host's cgroup namespace so cAdvisor can see every container's
    # CPU and memory usage, not just Alloy's own.
    cgroup: host
```

> `compose.observability.yaml` lines 104–112.

We mount the host's paths under `/host/...` rather than over the container's own `/proc` and `/sys`, so Alloy itself still runs normally; the exporters are told where to look.

The containerd socket path `/run/containerd/containerd.sock` is where Docker Engine and Docker Desktop keep it. On some Linux distributions it can be `/var/run/docker/containerd/containerd.sock`; check with `ls` if cAdvisor reports no containers.

## Step 2: Host metrics

Append to `config.alloy`:

```alloy
prometheus.exporter.unix "host" {
  procfs_path    = "/host/proc"
  sysfs_path     = "/host/sys"
  rootfs_path    = "/host/root"
  udev_data_path = "/host/root/run/udev/data"
}

// The exporter's default instance is Alloy's container hostname, which changes
// every time Alloy is recreated. A fixed name keeps one continuous series.
discovery.relabel "host" {
  targets = prometheus.exporter.unix.host.targets

  rule {
    target_label = "instance"
    replacement  = "docker-host"
  }
}

prometheus.scrape "host" {
  targets         = discovery.relabel.host.output
  job_name        = "node"
  scrape_interval = "15s"
  scrape_timeout  = "10s"
  forward_to      = [prometheus.remote_write.prometheus.receiver]
}
```

> `config.alloy` lines 423–447.

- The three `*_path` settings point the exporter at the mounted host views from Step 1.
- `udev_data_path` lets the disk collector look up device names. Docker Desktop's VM has no udev database, so on a Mac you'll see one harmless log line at startup: `Failed to open directory, disabling udev device properties`. Disk statistics still work.
- `discovery.relabel` sits between the exporter and the scrape purely to set `instance`. This is the standard way to change labels on an exporter's targets.
- As explained in Part 4, the series arrive with `job="integrations/unix"`, set by the exporter.

## Step 3: Container metrics

```alloy
// cAdvisor: CPU, memory and network per container, via the Docker socket.
prometheus.exporter.cadvisor "containers" {
  docker_host      = "unix:///var/run/docker.sock"
  docker_only      = true
  storage_duration = "2m"
}

discovery.relabel "containers" {
  targets = prometheus.exporter.cadvisor.containers.targets

  rule {
    target_label = "instance"
    replacement  = "docker-host"
  }
}

prometheus.scrape "containers" {
  targets         = discovery.relabel.containers.output
  job_name        = "cadvisor"
  scrape_interval = "15s"
  scrape_timeout  = "10s"
  forward_to      = [prometheus.remote_write.prometheus.receiver]
}
```

> `config.alloy` lines 449–471.

- **`docker_only = true`** reports Docker containers only, not every system cgroup in the VM. Without it you'd get hundreds of series for system processes you don't care about.
- **`storage_duration = "2m"`** is how long cAdvisor keeps its own in-memory history. Prometheus stores the long-term data, so cAdvisor only needs enough to answer the next scrape.
- Series arrive with `job="integrations/cadvisor"`. Each one carries the container `name` (such as `wispurl-gateway-1`) plus the container's Docker labels as `container_label_*`, including `container_label_com_docker_compose_service`. That lets you group by Compose service.

Validate, then recreate Alloy, since its Compose definition changed:

```sh
docker run --rm -e WISPURL_NETWORK=wispurl_wispurl-network \
  -v "$PWD/observability/alloy:/c:ro" grafana/alloy:v1.20.1 validate /c/config.alloy && echo valid
docker compose -f compose.observability.yaml up -d alloy
```

## The queries that matter

Here are the USE questions for each resource, with the PromQL to answer them. `node_*` metrics come from the host exporter and `container_*` metrics from cAdvisor.

| Resource | Question | PromQL |
| --- | --- | --- |
| Host CPU | Utilization | `1 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m]))` |
| | Saturation | `node_load1` compared with `count(node_cpu_seconds_total{mode="idle"})` |
| Host memory | Utilization | `1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes` |
| Host disk | Utilization | `1 - min(node_filesystem_avail_bytes{mountpoint=~"/\|/var/lib/docker", fstype!~"tmpfs\|erofs"} / node_filesystem_size_bytes{mountpoint=~"/\|/var/lib/docker", fstype!~"tmpfs\|erofs"})` |
| Host network | Errors | `sum(rate(node_network_receive_errs_total[5m]) + rate(node_network_transmit_errs_total[5m]))` |
| Containers | CPU per container (in cores) | `sum by (name) (rate(container_cpu_usage_seconds_total{name!=""}[5m]))` |
| | Memory per container | `sum by (name) (container_memory_working_set_bytes{name!=""})` |

Some of these deserve an explanation.

**CPU utilization.** `node_cpu_seconds_total` counts seconds each CPU spent in each mode (`idle`, `user`, `system` and so on). The idle rate is the fraction of time spent idle, so one minus the average idle rate is the fraction busy.

**Load as saturation.** The load average counts processes running or waiting for a CPU. If it's consistently above the number of CPUs, work is queuing. On the stack used for this series, `node_load1` was about 4 on a 10-CPU VM: busy, not saturated.

**`MemAvailable`, not `MemFree`.** Linux uses spare memory as disk cache, so "free" memory is always low on a healthy machine. `MemAvailable` estimates how much could be handed to programs without swapping, which is the number that matters.

**Which disk?** On a normal Linux host, Docker's data lives on the root filesystem `/`. On Docker Desktop, `/` inside the VM is a small read-only system image, and Docker's data lives on a separate virtual disk mounted at `/var/lib/docker`. The query watches whichever of the two exists and takes the fuller one (`min` of available space), so it works in both places. The `fstype` filter skips memory-backed and read-only system filesystems.

**Working set, not usage.** For containers, `container_memory_working_set_bytes` is memory the container actively uses, and it's the number the kernel compares against a memory limit when deciding what to kill. `container_memory_usage_bytes` includes reclaimable cache and overstates real use.

**`name!=""`** skips aggregate cgroups that have no container name.

## Check that it works

```promql
node_memory_MemTotal_bytes
```

One series, `instance="docker-host"`. On Docker Desktop, the value is the memory you gave Docker in its settings, not your computer's total.

```promql
count(node_cpu_seconds_total{mode="idle"})
```

The number of CPUs Docker can use.

```promql
topk(5, sum by (name) (container_memory_working_set_bytes{name!=""}))
```

The five most memory-hungry containers. On the stack built in this series, Grafana tops the list at about 540 MB, followed by Tempo, pgAdmin, Alloy and RabbitMQ, which is useful when deciding memory limits later.

```promql
count(count by (name) (container_cpu_usage_seconds_total{name!=""}))
```

The number of containers cAdvisor can see. It should match `docker ps -q | wc -l`. If it returns nothing, see the table below.

## When something goes wrong

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| No `container_*` series with a `name` | cAdvisor only sees Alloy's own cgroup | Add `cgroup: host` to the Alloy service and recreate it. |
| Alloy logs `Registration of the docker container factory failed ... containerd.sock` | containerd socket not mounted | Mount `/run/containerd/containerd.sock` (or your distribution's path). |
| Memory or disk numbers don't match your laptop | Docker Desktop VM | Expected. The metrics describe Docker's VM. |
| Several lines per graph for one host | `instance` changes when Alloy is recreated | Add the `discovery.relabel` that sets a fixed `instance`. |
| Disk query empty | No filesystem matches the mountpoints | Check `node_filesystem_size_bytes` for your real mountpoints and adjust the regex. |
| `Failed to open directory, disabling udev device properties` | No udev database in the VM | Harmless on Docker Desktop. |

## What you have now

- Host CPU, memory, disk and network metrics.
- Per-container CPU, memory and network metrics, labelled with container and Compose service names.
- A clear understanding of how much host access Alloy now has.
- The USE questions, and the PromQL to answer them.

That's a lot of metrics, and so far you've only seen them as numbers in Prometheus's query page. In [Part 6](06-deploy-grafana.md) we deploy Grafana, connect it to Prometheus as code, and start exploring visually.

## Key takeaways

- Use RED for services and USE (utilization, saturation, errors) for resources. Saturation is the most predictive and most often forgotten.
- On Docker Desktop, host metrics describe Docker's Linux VM, which is the limit your containers actually live within.
- cAdvisor in a container needs `cgroup: host`, or it silently reports only itself.
- Overwrite exporter `instance` labels with a stable name so recreating the collector doesn't split your series.
- Use `MemAvailable` for host memory and `working_set` for container memory.
- Host-level monitoring agents need broad host access. Treat them as highly trusted components.

## FAQ

### How do I get Docker container CPU and memory metrics in Prometheus?

Run cAdvisor, either as a container or embedded in Grafana Alloy (`prometheus.exporter.cadvisor`), and scrape it. Use `rate(container_cpu_usage_seconds_total[5m])` for CPU in cores and `container_memory_working_set_bytes` for memory, grouped by the `name` label.

### Why does cAdvisor show no containers when run inside Docker?

It's usually the cgroup namespace. Docker isolates each container's cgroups, so cAdvisor only sees its own. Run it with `cgroup: host` in Compose (or `--cgroupns=host` with `docker run`), and make sure it can reach the Docker and containerd sockets.

### What is the difference between node exporter and cAdvisor?

The node exporter reports on the whole machine: CPU, memory, disks, filesystems and network interfaces. cAdvisor reports per container: how much CPU, memory and network each container uses. You usually want both.

### Should I use container_memory_usage_bytes or working_set_bytes?

Use `container_memory_working_set_bytes`. It excludes inactive file cache that the kernel can reclaim, and it's the value compared against a container's memory limit when the out-of-memory killer decides what to stop. `container_memory_usage_bytes` includes cache and makes containers look larger than they are.

### Why do host metrics on Docker Desktop not match my computer?

Docker Desktop runs containers inside a Linux virtual machine. Containers, including the monitoring agent, can only see that VM, so CPU count, memory and disk reflect what Docker Desktop is allowed to use, set in its Resources settings.

---

**Series navigation:** Previous: [Part 4, Monitor PostgreSQL, Redis and RabbitMQ](04-monitor-postgres-redis-rabbitmq.md) · [Series index](README.md) · Next: [Part 6, Deploy Grafana](06-deploy-grafana.md)
