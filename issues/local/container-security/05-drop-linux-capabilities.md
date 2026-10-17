---
id: LOC-5.05
title: "Unnecessary Linux capabilities dropped (Compose and Kubernetes manifests)"
category: "5. Container Security (Local)"
status: todo
related:
  - docs/local/containers/container-00-multi-stage-application-images-and-runtime-hardening.md
  - docs/local/kubernetes/k8s-02-kind-manifests-and-workload-security-controls.md
---

# Unnecessary Linux capabilities dropped (Compose and Kubernetes manifests)

## What
Containers drop all Linux capabilities they don't need and cannot gain privileges.

## Current state
No `cap_drop` or `security_opt`; Vault adds `IPC_LOCK` even though `disable_mlock = true`.

## Subtasks
- [ ] `cap_drop: [ALL]` and `security_opt: [no-new-privileges:true]` for app services
- [ ] Remove `IPC_LOCK` from Vault or enable mlock (pick one consistently)
- [ ] Kubernetes `securityContext`: `capabilities.drop: [ALL]`, `allowPrivilegeEscalation: false`

## Acceptance criteria
- [ ] `docker inspect` shows CapDrop ALL for app services, and they still work
