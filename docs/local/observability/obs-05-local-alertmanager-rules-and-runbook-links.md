---
id: local-025
title: Local Alertmanager rules and runbook links
type: feat
feature: 6. Observability
status: not_started
depends_on: [local-020, local-021]
checklist_sections: 6. Observability; 7. Reliability and SRE
---

# Local Alertmanager rules and runbook links

## Goal
Add actionable local alerts and verify delivery with an explicit development receiver.

## Implementation subtasks
- [ ] Deploy and pin Alertmanager
- [ ] add rules for service unavailable, sustained elevated 5xx/latency, database unavailable, disk/volume pressure, RabbitMQ queue growth, Redis unavailable, Vault sealed, and telemetry pipeline down
- [ ] use duration thresholds to avoid flapping
- [ ] attach a runbook URL for each rule
- [ ] route local notifications to a documented webhook/log receiver and never require real Slack credentials
- [ ] prove grouping, deduplication, repeat interval, and resolve notification.

## Acceptance criteria
- [ ] Each rule loads successfully and fires under its controlled failure scenario
- [ ] every alert has severity, service, summary, description, and runbook link
- [ ] recovery resolves the alert
- [ ] no real external notification secret is required for local verification

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
