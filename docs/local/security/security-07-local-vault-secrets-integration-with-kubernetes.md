---
id: local-019
title: Local Vault secrets integration with Kubernetes
type: feat
feature: 9. Local Kubernetes and Packaging
status: not_started
depends_on: [local-007, local-016, local-017]
checklist_sections: 9. Local Kubernetes and Packaging
---

# Local Vault secrets integration with Kubernetes

## Goal
Connect the local Kubernetes workloads to Vault without placing root token or long-lived secret values in manifests.

## Implementation subtasks
- [ ] Choose and document External Secrets Operator or Vault Agent as the EKS-like local pattern
- [ ] use a Kubernetes auth role scoped by namespace and service account after Kind is ready
- [ ] map each service to only its KV path
- [ ] keep Vault CA trust mounted/configured
- [ ] use Kubernetes Secrets only as projected runtime delivery objects
- [ ] ensure generated values are excluded from Git and logs
- [ ] test token renewal and Vault outage behavior.

## Acceptance criteria
- [ ] A pod authenticates with its assigned service account
- [ ] it reads only its service path
- [ ] wrong namespace/account and cross-service reads are denied
- [ ] rotating a test value reaches the intended pod without exposing it in Git
- [ ] Vault outage behavior is bounded and documented
- [ ] ArgoCD reports no secret value in rendered manifests

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
