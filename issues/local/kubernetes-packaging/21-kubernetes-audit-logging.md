---
id: LOC-9.21
title: "Local Kubernetes audit logging enabled"
category: "9. Local Kubernetes and Packaging"
status: todo
related:
  - docs/local/kubernetes/k8s-00-kind-local-kubernetes-cluster-and-security-baseline.md
---

# Local Kubernetes audit logging enabled

## What
The API server writes audit logs, and they are collected.

## Current state
None.

## Subtasks
- [ ] Audit policy file (metadata for most, request/response for secrets and RBAC changes)
- [ ] kind `kubeadmConfigPatches` for `audit-policy-file` / `audit-log-path` with mounts
- [ ] Ship audit logs to Loki via Alloy

## Acceptance criteria
- [ ] Creating a Secret produces an audit entry visible in Loki
