---
id: LOC-9.19
title: "StatefulSets used for stateful components if not using external containers"
category: "9. Local Kubernetes and Packaging"
status: todo
related:
  - docs/local/kubernetes/k8s-02-kind-manifests-and-workload-security-controls.md
---

# StatefulSets used for stateful components if not using external containers

## What
Stateful components run as StatefulSets if hosted in-cluster, or the decision to keep them external is recorded.

## Current state
None.

## Subtasks
- [ ] Decide: in-cluster StatefulSets (own or Bitnami/operator charts) vs external Compose containers
- [ ] If in-cluster: StatefulSets with headless Services and volumeClaimTemplates for Postgres, RabbitMQ, Redis

## Acceptance criteria
- [ ] Decision recorded, and stateful components run as designed
