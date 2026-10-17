---
id: LOC-7.13
title: "Local rollback procedures tested and validated"
category: "7. Reliability and SRE (Local Validation)"
status: todo
related:
  - docs/local/sre/sre-02-slis-slos-error-budgets-and-local-rollback-policy.md
---

# Local rollback procedures tested and validated

## What
Rolling back a bad release is practised for Compose and Kubernetes.

## Current state
Images are untagged, so there is nothing to roll back to.

## Subtasks
- [ ] Tag images by SHA so a previous version can be redeployed in Compose
- [ ] Kubernetes: `helm rollback` / `argocd app rollback` to the previous revision
- [ ] Adopt expand/contract migrations so a rollback works with the newer schema
- [ ] Run and record a rollback drill

## Acceptance criteria
- [ ] A bad release is rolled back within the target time, with evidence
