---
id: LOC-4.13
title: "Pipeline stage: trigger local ArgoCD sync / Helm upgrade against the local Kubernetes cluster"
category: "4. Local CI/CD Pipeline (GitLab CI or Jenkins)"
status: todo
related:
  - docs/local/kubernetes/k8s-03-argocd-local-gitops-deployment.md
---

# Pipeline stage: trigger local ArgoCD sync / Helm upgrade against the local Kubernetes cluster

## What
The pipeline deploys by updating GitOps state and triggering an ArgoCD sync (or `helm upgrade`).

## Current state
No cluster or ArgoCD yet.

## Subtasks
- [ ] Update the image tag/digest in the environment values file (commit to the GitOps path)
- [ ] `argocd app sync` and `argocd app wait --health`
- [ ] Fallback path: `helm upgrade --install --atomic`

## Acceptance criteria
- [ ] A merged change reaches the cluster without manual kubectl
