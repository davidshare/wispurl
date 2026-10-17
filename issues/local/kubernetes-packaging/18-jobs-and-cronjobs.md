---
id: LOC-9.18
title: "Jobs and CronJobs configured for background tasks"
category: "9. Local Kubernetes and Packaging"
status: todo
related:
  - docs/local/kubernetes/k8s-02-kind-manifests-and-workload-security-controls.md
---

# Jobs and CronJobs configured for background tasks

## What
Background and one-off work runs as Jobs/CronJobs instead of long-running loops.

## Current state
cleanup-service loops with a sleep; migrations run in container entrypoints.

## Subtasks
- [ ] Add a single-sweep mode to cleanup-service and run it as a CronJob
- [ ] Run Alembic migrations as a Helm pre-install/pre-upgrade Job and remove them from entrypoints
- [ ] Postgres backup CronJob
- [ ] Set `concurrencyPolicy: Forbid`, history limits and `activeDeadlineSeconds`

## Acceptance criteria
- [ ] Cleanup runs on schedule, and migrations complete before app pods roll
