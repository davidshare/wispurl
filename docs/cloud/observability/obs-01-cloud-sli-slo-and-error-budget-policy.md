---
id: cloud-019
title: Cloud SLI/SLO and error-budget policy
type: feat
feature: 6. Observability
status: not_started
depends_on: [cloud-018]
checklist_sections: 6. Observability; 7. Reliability and SRE
---

# Cloud SLI/SLO and error-budget policy

## Goal
Turn provisional local objectives into measurable cloud SLOs with burn-rate alerts for the portfolio service.

## Implementation subtasks
- [ ] Define SLIs for public availability, link creation success and latency, redirect latency, analytics freshness, and dependency saturation
- [ ] choose rolling window/targets appropriate for demo
- [ ] define error budget and burn-rate alert thresholds
- [ ] link dashboards and runbooks
- [ ] explicitly state low traffic limitations and how synthetic probes supplement user traffic.

## Acceptance criteria
- [ ] Every SLO has queryable numerator/denominator, target/window, owner and dashboard
- [ ] burn-rate alert is tested with synthetic signal
- [ ] low-sample behavior is documented
- [ ] error budget policy defines when release promotion pauses

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
