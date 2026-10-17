---
id: LOC-9.05
title: "Local ArgoCD deployed and configured for GitOps synchronization"
category: "9. Local Kubernetes and Packaging"
status: todo
related:
  - docs/local/kubernetes/k8s-03-argocd-local-gitops-deployment.md
---

# Local ArgoCD deployed and configured for GitOps synchronization

## What
ArgoCD deploys the app from Git and keeps the cluster in sync.

## Current state
None.

## Subtasks
- [ ] Install pinned ArgoCD via Helm into the `argocd` namespace
- [ ] Create an AppProject restricting repos/namespaces
- [ ] Application(s) (app-of-apps) pointing at the chart path and env values
- [ ] Automated sync with prune + selfHeal for local
- [ ] Rotate the initial admin password; access via port-forward or ingress

## Acceptance criteria
- [ ] A Git change is reconciled into the cluster automatically, and manual drift is reverted
