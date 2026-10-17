---
id: LOC-5.08
title: "Local Kubernetes manifest scanning with Kubescape or KubeLinter"
category: "5. Container Security (Local)"
status: todo
related:
  - docs/local/security/security-08-kubernetes-manifest-security-scanning.md
---

# Local Kubernetes manifest scanning with Kubescape or KubeLinter

## What
Rendered Kubernetes manifests are scanned with Kubescape or KubeLinter before deploy.

## Current state
No manifests yet.

## Subtasks
- [ ] Render charts with `helm template` per environment
- [ ] Run `kube-linter lint` and/or `kubescape scan framework nsa,mitre`
- [ ] Fail CI on high findings, with documented exceptions

## Acceptance criteria
- [ ] A manifest missing a securityContext fails the scan
