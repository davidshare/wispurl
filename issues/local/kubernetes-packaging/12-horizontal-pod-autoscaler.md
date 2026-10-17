---
id: LOC-9.12
title: "Horizontal Pod Autoscaler configured (requires local metrics-server)"
category: "9. Local Kubernetes and Packaging"
status: todo
related:
  - docs/local/kubernetes/k8s-02-kind-manifests-and-workload-security-controls.md
---

# Horizontal Pod Autoscaler configured (requires local metrics-server)

## What
HPAs scale stateless services based on metrics.

## Current state
None.

## Subtasks
- [ ] Install metrics-server (`--kubelet-insecure-tls` on kind)
- [ ] HPAs for gateway, shortener and qr (CPU target, min/max replicas)
- [ ] Verify scaling under k6 load

## Acceptance criteria
- [ ] Load test triggers a scale-out and scale-in
