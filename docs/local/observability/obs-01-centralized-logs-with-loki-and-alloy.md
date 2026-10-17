---
id: local-022
title: Centralized logs with Loki and Alloy
type: feat
feature: 6. Observability
status: not_started
depends_on: []
checklist_sections: 6. Observability
---

# Centralized logs with Loki and Alloy

## Goal
Make Loki and Grafana Alloy provide searchable, labeled local logs for all application and infrastructure containers.

## Implementation subtasks
- [ ] Pin Loki image and bound retention
- [x] configure Alloy Docker discovery only for the project network
- [x] label logs with environment, Compose service, container and service identity
- [ ] preserve structured JSON fields
- [ ] redact Authorization headers, tokens, passwords, and Vault values before forwarding
- [ ] define behavior for multiline tracebacks and noisy health checks
- [ ] document the Docker socket read-only mount risk and why it is required
- [ ] make both services health-checked; Alloy currently uses `wget` in its Compose healthcheck, but the Alloy image does not contain `wget`, so the container reports unhealthy even though `/-/ready` returns HTTP 200 from the host.

## Acceptance criteria
- [ ] A request produces searchable gateway and downstream records sharing correlation/trace ID
- [ ] a synthetic secret is absent from ingested logs
- [ ] logs from all expected project containers arrive with stable labels
- [ ] retention is bounded
- [ ] stopped Loki makes Alloy unhealthy/retry and recovery resumes without unbounded disk growth

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
