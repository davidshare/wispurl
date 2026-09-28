---
id: local-030
title: Local failure injection and chaos validation
type: feat
feature: 7. Reliability and SRE
status: not_started
depends_on: [local-026, local-028]
checklist_sections: 7. Reliability and SRE
---

# Local failure injection and chaos validation

## Goal
Create repeatable local drills for service restart, dependency outage, duplicated messages, and database connection exhaustion.

## Implementation subtasks
- [ ] Add scripts or runbook procedures to restart a selected service during traffic
- [ ] stop PostgreSQL, Redis, RabbitMQ, Vault and telemetry dependencies one at a time
- [ ] inject duplicate RabbitMQ event
- [ ] reduce DB connection limit or exhaust pool
- [ ] observe health, retries, alerts, queue behavior and recovery
- [ ] keep drills isolated from developer data.

## Acceptance criteria
- [ ] Each of the four checklist scenarios has a repeatable procedure and expected outcome
- [ ] application recovers without manual data repair where designed
- [ ] alerts fire and clear
- [ ] no duplicate business side effect occurs
- [ ] evidence records measured recovery time and discovered follow-up fixes

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
