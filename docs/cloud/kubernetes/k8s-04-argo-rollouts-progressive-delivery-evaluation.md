---
id: cloud-029
title: Argo Rollouts progressive delivery evaluation
type: feat
feature: 5. Container Security
status: not_started
depends_on: [cloud-015, cloud-018]
checklist_sections: 5. Container Security; 10. Cloud Kubernetes
---

# Argo Rollouts progressive delivery evaluation

## Goal
Evaluate and implement a reversible progressive delivery path for the public gateway or shortener.

## Implementation subtasks
- [ ] Define canary steps and analysis metrics using request success and latency
- [ ] require sufficient baseline traffic or a synthetic traffic generator
- [ ] verify ALB integration supports the selected strategy
- [ ] set pause/abort thresholds and GitOps rollback
- [ ] include controller and telemetry costs
- [ ] if low traffic makes canary results invalid, use blue/green with synthetic checks and document why.

## Acceptance criteria
- [ ] A healthy release promotes
- [ ] an injected error/latency regression aborts promotion and restores prior ReplicaSet
- [ ] ArgoCD desired state matches rollout state
- [ ] analysis uses documented query/window
- [ ] low-volume data is not presented as statistically meaningful

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
