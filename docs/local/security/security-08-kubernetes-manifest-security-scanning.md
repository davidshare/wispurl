---
id: local-035
title: Kubernetes manifest security scanning
type: feat
feature: 5. Container Security
status: not_started
depends_on: [local-010, local-017]
checklist_sections: 5. Container Security
---

# Kubernetes manifest security scanning

## Goal
Add KubeLinter as the selected local Kubernetes manifest/chart scanner and make findings reviewable before deployment.

## Implementation subtasks
- [ ] Scan rendered Helm output for local and cloud-like values plus checked-in Kubernetes manifests
- [ ] fail on high/critical misconfiguration
- [ ] include workload securityContext, probes, resource requests/limits, image tags, host namespace/privilege, secret literals, and RBAC checks
- [ ] document justified exceptions with expiry and issue reference.

## Acceptance criteria
- [ ] CI scans every chart and manifest
- [ ] a deliberately privileged fixture fails
- [ ] actual findings are fixed or explicitly excepted
- [ ] generated report identifies file and resource
- [ ] scanner failure is a failed CI job

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
