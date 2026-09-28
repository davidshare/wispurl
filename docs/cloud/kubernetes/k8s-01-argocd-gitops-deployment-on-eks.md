---
id: cloud-015
title: ArgoCD GitOps deployment on EKS
type: feat
feature: 10. Cloud Kubernetes
status: not_started
depends_on: [cloud-004, cloud-014]
checklist_sections: 10. Cloud Kubernetes; 4. Cloud CI/CD
---

# ArgoCD GitOps deployment on EKS

## Goal
Install ArgoCD on EKS and use a protected GitOps path as the only routine mechanism for application deployment.

## Implementation subtasks
- [ ] Pin ArgoCD version/chart
- [ ] separate platform and application projects/namespaces
- [ ] configure SSO or protected access appropriate for demonstrator
- [ ] scope repo credentials read-only
- [ ] connect cloud Helm charts and per-environment values
- [ ] sync ordering handles CRDs, ESO, secrets, ingress then apps
- [ ] protect production-like sync with approval
- [ ] enable prune only for safe resources and preserve PVCs
- [ ] integrate GitHub Actions by commit update, not direct kubectl mutation.

## Acceptance criteria
- [ ] Fresh EKS cluster converges to healthy ArgoCD apps from a commit
- [ ] unauthorized project cannot modify cluster-scoped resources
- [ ] PR change is visible as diff and promotion is auditable
- [ ] revert commit restores prior revision
- [ ] secret values never appear in ArgoCD UI diff or Git

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
