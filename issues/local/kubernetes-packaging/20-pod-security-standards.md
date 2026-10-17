---
id: LOC-9.20
title: "Pod Security Standards (Restricted) enforced"
category: "9. Local Kubernetes and Packaging"
status: todo
related:
  - docs/local/kubernetes/k8s-02-kind-manifests-and-workload-security-controls.md
---

# Pod Security Standards (Restricted) enforced

## What
The Restricted Pod Security Standard is enforced on application namespaces.

## Current state
None.

## Subtasks
- [ ] Label namespaces `pod-security.kubernetes.io/enforce=restricted`
- [ ] securityContext: `runAsNonRoot`, `seccompProfile: RuntimeDefault`, drop ALL capabilities, `allowPrivilegeEscalation: false`
- [ ] Verify a non-compliant pod is rejected

## Acceptance criteria
- [ ] App namespaces enforce Restricted, and all app pods admit
