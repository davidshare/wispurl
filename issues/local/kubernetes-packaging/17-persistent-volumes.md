---
id: LOC-9.17
title: "PersistentVolumes and PersistentVolumeClaims defined for stateful components"
category: "9. Local Kubernetes and Packaging"
status: todo
related:
  - docs/local/kubernetes/k8s-02-kind-manifests-and-workload-security-controls.md
---

# PersistentVolumes and PersistentVolumeClaims defined for stateful components

## What
Stateful components keep their data across pod restarts via PVCs.

## Current state
None.

## Subtasks
- [ ] PVCs for Postgres, RabbitMQ, Vault (and Redis if persisted) using kind's `standard` StorageClass
- [ ] Verify data survives pod deletion

## Acceptance criteria
- [ ] Deleting a stateful pod loses no data
