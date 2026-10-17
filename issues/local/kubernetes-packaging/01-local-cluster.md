---
id: LOC-9.01
title: "Local Kubernetes cluster provisioned (kind, k3d, or minikube)"
category: "9. Local Kubernetes and Packaging"
status: todo
related:
  - docs/local/kubernetes/k8s-00-kind-local-kubernetes-cluster-and-security-baseline.md
---

# Local Kubernetes cluster provisioned (kind, k3d, or minikube)

## What
A reproducible local Kubernetes cluster (kind) defined in code.

## Current state
None.

## Subtasks
- [ ] `kind/cluster.yaml`: 1 control-plane + 2 workers, pinned node image
- [ ] `extraPortMappings` 80/443 for ingress
- [ ] Connect the local registry
- [ ] Audit policy mounts (see audit logging)
- [ ] `make kind-up` / `make kind-down`

## Acceptance criteria
- [ ] `make kind-up` creates a ready cluster from scratch
