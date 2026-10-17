---
id: local-036
title: PostgreSQL, Vault, and RabbitMQ recovery runbooks
type: feat
feature: 11. Operations and Incident Response
status: not_started
depends_on: [local-007, local-029, local-031]
checklist_sections: 11. Operations and Incident Response
---

# PostgreSQL, Vault, and RabbitMQ recovery runbooks

## Goal
Write command-level local recovery procedures for the three stateful systems, including safe diagnosis, recovery, and validation.

## Implementation subtasks
- [ ] For PostgreSQL document volume loss, backup selection, restore, migration check and service reconnect
- [ ] for Vault document sealed/uninitialized/keys lost/snapshot restore cases and root-token containment
- [ ] for RabbitMQ document definitions import, queue/message-loss limits, DLQ inspection and consumer restart
- [ ] state destructive steps, prerequisites, expected output and escalation point.

## Acceptance criteria
- [ ] A developer unfamiliar with internals can follow each procedure against disposable volumes
- [ ] restore result is validated by application-level smoke
- [ ] secrets are redacted
- [ ] commands match current Make/Compose targets
- [ ] data-loss boundaries and nonrecoverable cases are explicit

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
