---
id: cloud-017
title: EKS network policy, RBAC, pod security, and runtime protection
type: feat
feature: 5. Container Security
status: not_started
depends_on: [cloud-004, cloud-016]
checklist_sections: 5. Container Security; 10. Cloud Kubernetes; 11. Security
---

# EKS network policy, RBAC, pod security, and runtime protection

## Goal
Enforce workload admission and network boundaries consistently across EKS namespaces.

## Implementation subtasks
- [ ] Apply Restricted Pod Security
- [ ] define service accounts with namespace-scoped RBAC and no application cluster-admin
- [ ] install Kyverno or Gatekeeper policy alongside signature policy
- [ ] configure VPC CNI NetworkPolicy support and default-deny policies with explicit DNS, ingress, app-to-data, ESO and telemetry flows
- [ ] configure Falco or AWS-native runtime threat detection and route alerts to monitored destination
- [ ] document policy exception process and expiration.

## Acceptance criteria
- [ ] A privileged container and broad RBAC fixture are rejected
- [ ] service namespace cannot reach unrelated data service
- [ ] required app flows work
- [ ] runtime test behavior produces alert
- [ ] all exceptions have owner/reason/expiry
- [ ] policy checks run in CI and on admission

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
