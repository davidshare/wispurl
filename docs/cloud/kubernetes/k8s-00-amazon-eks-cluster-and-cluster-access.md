---
id: cloud-004
title: Amazon EKS cluster and cluster access
type: feat
feature: 10. Cloud Kubernetes
status: not_started
depends_on: [cloud-001, cloud-002]
checklist_sections: 10. Cloud Kubernetes; 7. Reliability and SRE
---

# Amazon EKS cluster and cluster access

## Goal
Provision a production-style but cost-bounded EKS cluster for the portfolio workload.

## Implementation subtasks
- [ ] Use private subnets across at least two AZs
- [ ] define version-pinned EKS control plane and managed node groups with small autoscaled capacity
- [ ] enable control-plane audit/authenticator logs to CloudWatch
- [ ] use EKS access entries/IAM roles rather than static kubeconfigs
- [ ] configure IRSA OIDC provider
- [ ] define cluster endpoint access policy
- [ ] enable encryption for Kubernetes secrets
- [ ] install and configure Cluster Autoscaler or Karpenter after recording cost/complexity choice
- [ ] tag cluster/nodes, set budgets, and document teardown.

## Acceptance criteria
- [ ] Cluster provisions from Terraform
- [ ] only approved IAM role can administer
- [ ] workload role has no cluster-admin
- [ ] audit event reaches CloudWatch
- [ ] node group scales from minimum using the selected autoscaler and can scale to zero or has a documented cost reason
- [ ] no public DB/data plane access
- [ ] teardown preserves shared state bucket only

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
