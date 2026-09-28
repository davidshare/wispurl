---
id: local-016
title: Kind local Kubernetes cluster and security baseline
type: feat
feature: 9. Local Kubernetes and Packaging
status: not_started
depends_on: []
checklist_sections: 9. Local Kubernetes and Packaging; 5. Container Security; 10. Security and Compliance
---

# Kind local Kubernetes cluster and security baseline

## Goal
Provision a reproducible Kind cluster profile for local E2E and GitOps work, with security and capacity settings sized for developer laptops.

## Implementation subtasks
- [ ] Pin Kind and Kubernetes node image versions
- [ ] provision a named cluster with separate application, data, and observability namespaces
- [ ] install metrics-server for HPA
- [ ] define ResourceQuota and LimitRange
- [ ] configure Kubernetes API audit policy and mount audit output from Kind nodes to an ignored host path without recording secret request bodies
- [ ] enable default-deny ingress and egress NetworkPolicies after required DNS and service flows are enumerated
- [ ] enforce Restricted Pod Security Standards
- [ ] define local TLS trust approach
- [ ] document create/destroy and data-loss boundaries.

## Acceptance criteria
- [ ] A clean machine can create and remove cluster using documented pinned versions
- [ ] namespaces, metrics-server and policies are inspectable
- [ ] restricted workload passes and privileged workload is rejected
- [ ] default-deny blocks an unapproved namespace flow
- [ ] limits prevent a test workload from consuming all cluster resources
- [ ] a test API request appears in the audit log without secret values

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
