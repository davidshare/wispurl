---
title: "Observability for WispURL, Part 16: Runbooks for Every Alert"
seo_title: "How to Write Runbooks for Prometheus Alerts (With Template)"
slug: runbooks-for-prometheus-alerts-template
description: "Write a runbook for every Prometheus alert: a simple template, where to keep runbooks, how to link them with runbook_url, and how to keep them current."
series: "Observability for WispURL"
part: 16
date: 2026-10-17
last_updated: 2026-10-17
author: David Essien
tags: [sre, runbooks, alerting, incident-response, prometheus, documentation]
keywords:
  - "how to write a runbook"
  - "runbook template SRE"
  - "Prometheus runbook_url annotation"
  - "alert runbook examples"
  - "incident response runbook"
  - "docs as code runbooks"
difficulty: beginner
estimated_time: 30 minutes
prerequisites:
  - "Part 15: Alerting with Prometheus and Alertmanager"
repo_files:
  - docs/runbooks/
  - observability/prometheus/rules/wispurl-alerts.yml
---

# Observability for WispURL, Part 16: Runbooks for Every Alert

> **In short:** every alert should link to a runbook through its `runbook_url` annotation. Keep runbooks as Markdown files in the same repository as the alert rules (`docs/runbooks/`), one per alert, all using one template: what it means, impact, how to confirm, how to fix, and what to do afterwards. Write for someone tired and unfamiliar with the system: exact commands, real queries, links to the right dashboard. Check in CI that every rule's runbook exists, and update the page after every incident.

You now have alerts that fire for the right reasons and reach the right people. But an alert only says *what* is wrong. At 3 a.m. the person receiving it needs to know what it means, how bad it is, how to confirm it, and what to do. That's a **runbook**. In this final part you'll learn how to write them, where to keep them, and how to stop them going stale.

## Design decisions

### One runbook per alert

Some teams keep one large "operations guide". When an alert fires, nobody wants to search a long document. One page per alert, linked directly from the alert, means the right instructions are one click away from the notification.

### Keep runbooks next to the rules

Runbooks could live in a wiki, Confluence or Notion. We keep them as Markdown in the repository, in `docs/runbooks/`, next to `observability/prometheus/rules/wispurl-alerts.yml`, because:

- **They change together.** Renaming an alert or changing its threshold happens in the same pull request as updating its runbook, and reviewers can see both.
- **History is free.** Git shows when and why a step was added.
- **They can be checked automatically.** A script can confirm every alert has a runbook (below).

The trade-off is that people without repository access can't edit them. For an engineering team that owns the system, that's usually acceptable.

### Link with an absolute URL

The alert's `runbook_url` is a full GitHub URL:

```yaml
runbook_url: "https://github.com/davidshare/wispurl/blob/master/docs/runbooks/dead-letter-queue-not-empty.md"
```

A relative path wouldn't work from an email or a phone. The URL points at the `master` branch, so a runbook change is live as soon as it's merged.

### Write for someone tired and new

The person reading a runbook may have joined last week, be half asleep, and be under pressure. So runbooks should:

- say plainly what the alert means and who is affected;
- give **exact** commands and queries that can be copied, not "check the logs";
- link to the relevant dashboard or query;
- give the safe, common fixes first;
- avoid needing knowledge that isn't on the page.

## Step 1: A template

Every WispURL runbook has the same five sections:

```markdown
# <AlertName>

**Severity:** critical | warning
**Defined in:** observability/prometheus/rules/wispurl-alerts.yml

## What it means
One or two sentences: which condition triggered this, in plain words.

## Impact
Who or what is affected right now, and how badly.

## How to confirm
Numbered steps with exact commands, PromQL or LogQL, and links,
to check the alert is real and find the cause.

## How to fix
The likely causes, each with the fix. Safe, common fixes first.

## After it's fixed
How to confirm it's resolved, and a reminder to update this page.
```

A predictable layout matters more than perfect prose. Under pressure, people scan for "How to fix", and it should always be in the same place.

## Step 2: A worked example

Here is the runbook for the dead-letter queue alert from Part 15:

```markdown
# DeadLetterQueueNotEmpty

**Severity:** warning
**Defined in:** observability/prometheus/rules/wispurl-alerts.yml

## What it means

At least one event has landed in `events.dlq` after failing processing on every retry.

## Impact

That event's work did not happen: a click was not counted, or a notification was not sent.

## How to confirm

1. Open RabbitMQ management at http://127.0.0.1:15672, queue `events.dlq`,
   and use **Get messages** to read one.
2. Find the failure in the consumer's logs:
   `{service=~"analytics-consumer-service|notification-service", level=~"error|warning"} |= "event_dropped_to_dlq"`.
3. Open the trace linked from that log line to see the failing span.

## How to fix

- Fix the bug or dependency that caused the failure first.
- Then move the messages back for reprocessing and confirm the queue drains to 0. ...
```

> `docs/runbooks/dead-letter-queue-not-empty.md`.

Notice how it uses everything the series built:

- **Step 2 of "How to confirm"** is a LogQL query using the labels from Part 8 (`service`, `level`) and the event name the messaging code logs.
- **Step 3** uses the log-to-trace link from Part 13. The failed attempts are spans in the original trace (Part 11), with the exception recorded on them.
- **"How to fix"** says what to do *first* (fix the cause) before the tempting shortcut (replaying the messages, which would just fail again).

The runbooks for alerts about missing data spell out the surprise. `ServiceDisappeared` explains why the service shows up as *missing* rather than *down*: stopped containers drop out of Docker discovery. Otherwise the reader may waste time looking for a failed scrape that never happened.

## Step 3: One runbook for every alert

`docs/runbooks/` has one file per alert, plus an index:

| Alert | Severity | Runbook |
| --- | --- | --- |
| TargetDown | critical | `target-down.md` |
| ServiceDisappeared | critical | `service-disappeared.md` |
| MetricsPipelineDown | critical | `metrics-pipeline-down.md` |
| HighErrorRate | warning | `high-error-rate.md` |
| HighLatencyP95 | warning | `high-latency.md` |
| PostgresDown | critical | `postgres-down.md` |
| PostgresConnectionsHigh | warning | `postgres-connections-high.md` |
| RedisDown | critical | `redis-down.md` |
| DeadLetterQueueNotEmpty | warning | `dead-letter-queue-not-empty.md` |
| QueueBacklogGrowing | warning | `queue-backlog-growing.md` |
| HostDiskAlmostFull | warning | `host-disk-almost-full.md` |

> `docs/runbooks/README.md`.

A few examples of the "how to confirm" steps, to show the level of detail:

- **HighLatencyP95** points at the RED dashboard, then gives a TraceQL query for the slow requests (`{resource.service.name="<service>" && duration > 1s}`) and says what to look for: which span takes the time, whether it's a SQL query, a Redis call or a downstream service.
- **PostgresConnectionsHigh** gives the exact `psql` query that groups `pg_stat_activity` by user, application and state, and explains that many `idle in transaction` connections point to a code path not closing transactions.
- **MetricsPipelineDown** starts with the Alloy UI at http://127.0.0.1:12345, where unhealthy components show in red.

## Step 4: Link every alert to its runbook

Each rule's annotations include its runbook:

```yaml
        annotations:
          summary: "{{ $value }} message(s) in the dead-letter queue"
          description: "Events failed processing after all retries and were dead-lettered."
          runbook_url: "https://github.com/davidshare/wispurl/blob/master/docs/runbooks/dead-letter-queue-not-empty.md"
```

> `observability/prometheus/rules/wispurl-alerts.yml`, in each rule.

`runbook_url` is a convention, not a special field, but it's widely recognised: Alertmanager includes it in notifications, and Grafana's alert views show it as a link.

## Step 5: Check that every alert has a runbook

Runbooks rot in two ways: an alert is added without one, or a file is renamed and the link breaks. Both can be checked automatically. This short script fails if any rule lacks a `runbook_url` or points at a file that doesn't exist:

```sh
python3 - <<'EOF'
import re, sys, pathlib
rules = pathlib.Path("observability/prometheus/rules/wispurl-alerts.yml").read_text()
alerts = re.findall(r"- alert: (\w+)", rules)
links = re.findall(r"runbook_url: \"https://github.com/[^/]+/[^/]+/blob/[^/]+/(docs/runbooks/[\w-]+\.md)\"", rules)
missing_files = [l for l in links if not pathlib.Path(l).exists()]
print(f"{len(alerts)} alerts, {len(links)} runbook links")
if len(links) != len(alerts) or missing_files:
    print("missing:", missing_files or "some alerts have no runbook_url"); sys.exit(1)
print("every alert has a runbook")
EOF
```

```text
11 alerts, 11 runbook links
every alert has a runbook
```

Run it in CI (the project's CI pipeline is a separate series) so a pull request that adds an alert without a runbook fails.

## Keeping runbooks accurate

A wrong runbook is worse than none, because people trust it. A few habits keep them honest:

- **Update after every incident.** The last section of each runbook says so. The best time to fix a runbook is right after someone has followed it and found a missing step.
- **Review them in post-incident reviews.** "Did the runbook help?" is a standard question.
- **Practise.** The final check below is a fire drill: break something on purpose and follow the runbook. Steps that don't work show up immediately, without a real outage.
- **Delete alerts nobody acts on.** If a runbook's honest "how to fix" is "nothing, it resolves itself", the alert shouldn't page anyone.

## Check that it works

Run a small fire drill with the alert from Part 15:

1. Stop a service: `docker compose stop qr-service`.
2. Wait for the `ServiceDisappeared` email in Mailpit (http://127.0.0.1:8025), about three minutes.
3. Open the email and follow its runbook link.
4. Follow the runbook **exactly as written**: `docker compose ps -a qr-service`, then `docker compose logs --tail 100 qr-service`, then `docker compose up -d qr-service`.
5. Confirm the `[RESOLVED]` email arrives.

If any step was unclear or wrong, fix the runbook in the same sitting. That's the habit this part is really about.

## The series in review

Across seventeen parts, you've built a complete, self-hosted observability platform for a microservices application, and learned the reasoning behind each piece:

| Signal | Produced by | Collected by | Stored in | Used for |
| --- | --- | --- | --- | --- |
| Metrics | Shared middleware (Part 2), embedded exporters (Parts 4–5) | Alloy (Part 3) | Prometheus (Part 1) | Dashboards (Part 14), alerts (Part 15) |
| Logs | Structured JSON logging (Part 8) | Alloy, with redaction and parsing (Part 8) | Loki (Part 7) | Investigation, linked to traces (Part 13) |
| Traces | OpenTelemetry (Parts 10–12) | Alloy (Part 9) | Tempo (Part 9) | Following requests across services and queues (Part 11) |

And the principles that carry over to any system:

- **Pin versions, validate configs, and keep everything in Git**, dashboards and data sources included.
- **Keep labels low-cardinality**; put IDs in logs and traces, not metric or log labels.
- **Use one name per service** across metrics, logs and traces, so they can be linked.
- **Collect through one pipeline** that the application talks to, so backends can change.
- **Never let observability hurt the system it observes**: background export, bounded queues, rate limits.
- **Design for missing data**: monitor the collector, and alert when things disappear, not just when they fail.
- **Alert on symptoms, and make every alert actionable** with a runbook.

The same stack moves to the cloud with the same protocols: Amazon Managed Service for Prometheus, Amazon Managed Grafana, and object storage for Loki and Tempo. That's the subject of the cloud series.

## Key takeaways

- Every alert needs a runbook, linked with `runbook_url`.
- Keep runbooks as Markdown next to the alert rules, so they change and are reviewed together.
- Use one template: what it means, impact, how to confirm, how to fix, after it's fixed.
- Write exact commands and queries for a tired reader unfamiliar with the system.
- Check automatically that every alert has an existing runbook.
- Keep runbooks alive: update them after incidents and test them with fire drills.

## FAQ

### What is a runbook in SRE?

A short document describing how to respond to a specific alert or operational situation: what it means, its impact, how to confirm it, and the steps to fix it. Linking runbooks directly from alerts reduces response time and lets people who don't know a system well handle incidents.

### How do I add a runbook link to a Prometheus alert?

Add a `runbook_url` annotation to the rule, for example `runbook_url: "https://github.com/org/repo/blob/main/docs/runbooks/high-error-rate.md"`. Alertmanager includes annotations in notifications, and Grafana displays `runbook_url` as a link.

### What should a runbook template include?

The alert name and severity, what the alert means, its impact, numbered steps to confirm the problem (with exact commands and queries), likely causes with their fixes, and how to verify the fix. A consistent structure matters more than length.

### Where should runbooks be stored?

Somewhere they can be updated alongside the alerts they describe and reached from a notification on any device. Storing Markdown runbooks in the same Git repository as the alert rules lets one pull request change both, and lets CI check that every alert has a runbook.

### How do you keep runbooks up to date?

Update the runbook right after every incident that used it, review runbooks during post-incident reviews, run fire drills that follow them step by step, and check automatically that every alert links to an existing runbook.

---

**Series navigation:** Previous: [Part 15, Alerting with Prometheus and Alertmanager](15-alerting-with-alertmanager.md) · [Series index](README.md)
