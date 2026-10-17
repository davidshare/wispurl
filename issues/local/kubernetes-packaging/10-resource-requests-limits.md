---
id: LOC-9.10
title: "Resource requests and limits explicitly defined for all pods"
category: "9. Local Kubernetes and Packaging"
status: todo
related:
  - docs/local/kubernetes/k8s-02-kind-manifests-and-workload-security-controls.md
---

# Resource requests and limits explicitly defined for all pods

## What
Every pod declares CPU/memory requests and limits.

## Current state
None.

## Subtasks
- [ ] Requests/limits for every container from measured baselines
- [ ] LimitRange and ResourceQuota per namespace

## Acceptance criteria
- [ ] A pod without resources is rejected or defaulted by LimitRange
