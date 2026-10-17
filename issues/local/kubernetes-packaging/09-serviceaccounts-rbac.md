---
id: LOC-9.09
title: "ServiceAccounts and local RBAC policies defined"
category: "9. Local Kubernetes and Packaging"
status: todo
related:
  - docs/local/kubernetes/k8s-02-kind-manifests-and-workload-security-controls.md
---

# ServiceAccounts and local RBAC policies defined

## What
Each workload has its own ServiceAccount with minimal RBAC.

## Current state
None.

## Subtasks
- [ ] One ServiceAccount per service
- [ ] `automountServiceAccountToken: false` unless needed
- [ ] Minimal Roles/RoleBindings, with no cluster-wide rights for apps
- [ ] Verify with `kubectl auth can-i --as=system:serviceaccount:...`

## Acceptance criteria
- [ ] No app ServiceAccount can list secrets or act cluster-wide
