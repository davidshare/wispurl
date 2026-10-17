---
id: cloud-005
title: AWS application workload identity and secret projection
type: feat
feature: 2. Secrets Management
status: not_started
depends_on: [cloud-003, cloud-004]
checklist_sections: 2. Secrets Management; 10. Cloud Kubernetes
---

# AWS application workload identity and secret projection

## Goal
Integrate AWS Secrets Manager with EKS workloads through IRSA and External Secrets Operator; this is the workload-side issue separate from secret-store setup.

## Implementation subtasks
- [ ] Install pinned External Secrets Operator with namespace-scoped permissions
- [ ] define SecretStore/ExternalSecret per namespace and service
- [ ] bind each service account to the narrow Secrets Manager ARN and KMS decrypt permission
- [ ] rotate projected RDS credentials and prove pod update/restart strategy
- [ ] ensure ArgoCD never stores resolved values in Git/rendered output
- [ ] define startup behavior on missing or unavailable secret.

## Acceptance criteria
- [ ] Every application pod receives only its own keys
- [ ] unauthorized service account cannot fetch another secret
- [ ] no secret value appears in Git, Helm values, Terraform plan or ArgoCD diff
- [ ] rotation updates a test workload and restores DB connection
- [ ] ESO reports clear status for missing secret without dumping values

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
