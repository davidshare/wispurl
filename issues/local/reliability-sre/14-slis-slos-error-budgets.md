---
id: LOC-7.14
title: "SLIs/SLOs/error budgets drafted (even provisionally) so cloud thresholds aren't invented from scratch later"
category: "7. Reliability and SRE (Local Validation)"
status: todo
related:
  - docs/local/sre/sre-02-slis-slos-error-budgets-and-local-rollback-policy.md
---

# SLIs/SLOs/error budgets drafted (even provisionally) so cloud thresholds aren't invented from scratch later

## What
Provisional SLIs, SLOs and error budgets exist so cloud thresholds are based on data.

## Current state
None.

## Subtasks
- [ ] Define SLIs: redirect availability and latency, API availability, analytics event freshness lag
- [ ] Set provisional SLO targets and error budgets
- [ ] Add Prometheus recording rules and burn-rate alerts
- [ ] Write `docs/sre/slo.md` including the rollback/freeze policy

## Acceptance criteria
- [ ] SLO doc reviewed, and recording rules produce the SLI series
