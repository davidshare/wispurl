---
id: cloud-032
title: Cloud service ownership, status view, and response guide
type: feat
feature: 7. Reliability and SRE
status: not_started
depends_on: [cloud-018, cloud-022]
checklist_sections: 7. Reliability and SRE; 12. Operations
---

# Cloud service ownership, status view, and response guide

## Goal
Make service ownership and operational state visible during deployments, incidents, and maintenance.

## Implementation subtasks
- [ ] Assign owner for each application and managed dependency
- [ ] define severity and escalation route
- [ ] create an internal status view from CloudWatch/health probes that exposes no secret or customer data
- [ ] define maintenance/change approval and incident update cadence
- [ ] link status view and service runbooks from alerts
- [ ] use a no-cost demonstrator escalation substitute unless paid paging is explicitly budgeted.

## Acceptance criteria
- [ ] Every service/dependency has an owner
- [ ] status view reflects a controlled failure within the documented interval
- [ ] no credential/customer data is exposed
- [ ] maintenance and incident response are exercised in a tabletop
- [ ] alert links resolve to the correct service runbook

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
