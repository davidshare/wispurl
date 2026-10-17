---
id: LOC-11.03
title: "Local rollback runbook created"
category: "11. Operations and Incident Response (Local)"
status: todo
related:
  - docs/local/sre/sre-06-local-operational-guide-and-troubleshooting.md
---

# Local rollback runbook created

## What
A local rollback runbook.

## Current state
None.

## Subtasks
- [ ] Decide when to roll back (SLO/alert triggers)
- [ ] Compose rollback to the previous SHA tag
- [ ] `helm rollback` / `argocd app rollback`
- [ ] Migration compatibility checks and verification

## Acceptance criteria
- [ ] Rollback drill performed from the runbook
