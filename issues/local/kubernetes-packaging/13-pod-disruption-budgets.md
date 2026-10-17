---
id: LOC-9.13
title: "Pod Disruption Budgets defined"
category: "9. Local Kubernetes and Packaging"
status: todo
related:
  - docs/local/kubernetes/k8s-02-kind-manifests-and-workload-security-controls.md
---

# Pod Disruption Budgets defined

## What
PDBs keep multi-replica services available during voluntary disruptions.

## Current state
None.

## Subtasks
- [ ] PDB (`minAvailable: 1` or `maxUnavailable: 1`) for every multi-replica service
- [ ] Test with `kubectl drain` on a worker node

## Acceptance criteria
- [ ] Node drain never takes a service to zero ready pods
