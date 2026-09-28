---
id: local-033
title: SLIs, SLOs, error budgets, and local rollback policy
type: feat
feature: 7. Reliability and SRE
status: not_started
depends_on: []
checklist_sections: 7. Reliability and SRE; 8. Backups and Disaster Recovery
---

# SLIs, SLOs, error budgets, and local rollback policy

## Goal
Define provisional service-level objectives from the project’s actual user journeys so later AWS thresholds have a measured baseline.

## Implementation subtasks
- [ ] Set SLIs for gateway availability, link creation success/latency, redirect latency, analytics ingestion freshness, and dependency availability
- [ ] set provisional target/window and excluded planned downtime
- [ ] define burn-rate alert intent
- [ ] record local measurement limitations
- [ ] define rollback trigger and recovery command for Compose and Kind releases.

## Acceptance criteria
- [ ] Every SLI has numerator/denominator, source metric, service owner and measurement window
- [ ] provisional SLO values are explicitly marked assumptions
- [ ] error budget calculation can be reproduced
- [ ] rollback trigger is tied to an observable failed health/smoke condition and has been exercised

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
