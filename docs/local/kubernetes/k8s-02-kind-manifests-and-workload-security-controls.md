---
id: local-034
title: Kind manifests and workload security controls
type: feat
feature: 9. Local Kubernetes and Packaging
status: not_started
depends_on: [local-016, local-017]
checklist_sections: 9. Local Kubernetes and Packaging; 10. Security and Compliance
---

# Kind manifests and workload security controls

## Goal
Complete Kubernetes packaging requirements that apply across all WispURL and stateful workloads.

## Implementation subtasks
- [ ] Use separate namespaces and service accounts
- [ ] define namespace-scoped RBAC with no app cluster-admin
- [ ] set requests/limits and probes on every pod
- [ ] apply Restricted Pod Security
- [ ] default-deny network policies with explicit DNS, gateway-to-service, app-to-data, observability and Vault flows
- [ ] configure TLS for ingress and Vault
- [ ] PVCs for stateful services
- [ ] Jobs/CronJobs for one-shot initialization and cleanup
- [ ] PDBs for replicated stateless workloads
- [ ] HPA only for services with metrics-server and meaningful scaling signals
- [ ] document single-replica workloads where PDB/HPA offers no value.

## Acceptance criteria
- [ ] KubeLinter/Kubescape scan has no unexplained high-severity findings
- [ ] application identities cannot read cluster-wide resources
- [ ] network tests prove only required flows work
- [ ] all pods have probes and resource bounds
- [ ] Restricted policy accepts application pods
- [ ] persistent workloads mount PVC
- [ ] HPA scales a test deployment using metrics-server

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
