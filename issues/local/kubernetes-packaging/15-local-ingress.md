---
id: LOC-9.15
title: "Local Ingress configured (e.g., ingress-nginx)"
category: "9. Local Kubernetes and Packaging"
status: todo
related:
  - docs/local/kubernetes/k8s-02-kind-manifests-and-workload-security-controls.md
---

# Local Ingress configured (e.g., ingress-nginx)

## What
An ingress controller exposes the frontend and API on local hostnames.

## Current state
None.

## Subtasks
- [ ] Install ingress-nginx for kind
- [ ] Ingress rules: `wispurl.local` → frontend, `api.wispurl.local` → gateway
- [ ] Document the `/etc/hosts` entries

## Acceptance criteria
- [ ] The app works in a browser via the ingress hostnames
