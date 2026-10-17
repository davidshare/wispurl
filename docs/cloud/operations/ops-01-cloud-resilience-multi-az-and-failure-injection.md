---
id: cloud-021
title: Cloud resilience, multi-AZ and failure injection
type: feat
feature: 7. Reliability and SRE
status: not_started
depends_on: [cloud-004, cloud-018]
checklist_sections: 7. Reliability and SRE
---

# Cloud resilience, multi-AZ and failure injection

## Goal
Demonstrate controlled availability and recovery behavior across AZ, pod, node and managed dependency failures.

## Implementation subtasks
- [ ] Place critical control/data plane across at least two AZs where service tier allows
- [ ] configure replicas, PDB, autoscaling and topology spread
- [ ] schedule safe pod kill/node drain exercises
- [ ] test RDS failover, Redis interruption and broker unavailable
- [ ] define maintenance windows and change approvals
- [ ] use rollback triggers from failed health/smoke and document any single-AZ/cost exception.

## Acceptance criteria
- [ ] Pod/node disruption preserves public user journey within target
- [ ] dependency failure produces documented degraded behavior and alert
- [ ] RDS failover reconnects within measured time
- [ ] rollback restores prior version
- [ ] drill artifacts record impact, detection, recovery and action items

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
