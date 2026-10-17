---
id: LOC-6.09
title: "Log collection/forwarding via Grafana Alloy or Fluent Bit"
category: "6. Observability (Local Stack)"
status: done
related:
  - docs/local/observability/obs-01-centralized-logs-with-loki-and-alloy.md
---

# Log collection/forwarding via Grafana Alloy or Fluent Bit

## What
Grafana Alloy discovers project containers and forwards their logs to Loki with stable labels.

## Current state
`discovery.docker` + `loki.source.docker` limited to `wispurl_wispurl-network`, labelled with service, container, environment and application.

## Subtasks
- [x] Docker discovery via read-only socket
- [x] Filter to the project network
- [x] Stable labels (service, container, environment, application)
- [x] Forward to Loki

## Acceptance criteria
- [x] Logs from all project containers arrive in Loki with these labels

## Follow-ups
- [x] Fix the Alloy healthcheck: the image has no `wget`, so the container is always unhealthy — use a check the image supports or remove it
- [ ] Add a `loki.process` pipeline that parses the JSON log line (`stage.json`) and promotes only `level` to a label; keep `request_id`/`trace_id` as structured metadata, not labels
- [ ] Redact secrets before forwarding (`stage.replace` for `Authorization`/Bearer tokens, passwords, DSNs, Vault tokens) and verify a synthetic secret never reaches Loki
- [ ] Join multi-line Python tracebacks into one entry (`stage.multiline`)
- [ ] Drop or sample `/health` and `/metrics` access-log noise (`stage.drop`)
- [ ] Document why Alloy mounts the Docker socket read-only and the risk it carries (feed into the [threat model](../security-compliance/04-threat-model.md))

## References
- [observability/alloy/config.alloy](../../../observability/alloy/config.alloy)
- [compose.observability.yaml](../../../compose.observability.yaml)
