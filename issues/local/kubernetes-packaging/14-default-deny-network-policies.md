---
id: LOC-9.14
title: "Default-deny NetworkPolicies applied"
category: "9. Local Kubernetes and Packaging"
status: todo
related:
  - docs/local/kubernetes/k8s-02-kind-manifests-and-workload-security-controls.md
---

# Default-deny NetworkPolicies applied

## What
Default-deny NetworkPolicies with explicit allows for each required flow.

## Current state
None. kind's default CNI does not enforce NetworkPolicy.

## Subtasks
- [ ] Install a policy-enforcing CNI (Calico or Cilium) in kind
- [ ] Default-deny ingress and egress per namespace, plus a DNS allow
- [ ] Allow only required flows (ingress → gateway/frontend, gateway → auth/shortener/analytics/qr, shortener → rate-limiter/analytics/RabbitMQ/Postgres, etc.)
- [ ] Verify blocked flows fail (e.g. frontend → Postgres)

## Acceptance criteria
- [ ] Unlisted pod-to-pod traffic is denied, and the app still works
