---
id: LOC-5.04
title: "Read-only root filesystems where application logic permits"
category: "5. Container Security (Local)"
status: todo
related:
  - docs/local/containers/container-00-multi-stage-application-images-and-runtime-hardening.md
  - docs/local/kubernetes/k8s-02-kind-manifests-and-workload-security-controls.md
---

# Read-only root filesystems where application logic permits

## What
Containers run with a read-only root filesystem, with writable tmpfs only where needed.

## Current state
Not set anywhere.

## Subtasks
- [ ] Set `read_only: true` for app services in Compose
- [ ] Add `tmpfs` for `/tmp` (and the Next.js cache dir for the frontend)
- [ ] Verify each service starts and serves traffic
- [ ] Set `readOnlyRootFilesystem: true` in Helm templates

## Acceptance criteria
- [ ] All app services run with a read-only rootfs in Compose and Kubernetes
