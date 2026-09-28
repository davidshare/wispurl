---
id: cloud-031
title: AWS cloud threat model and accepted risks
type: feat
feature: 11. Security and Compliance
status: not_started
depends_on: []
checklist_sections: 11. Security and Compliance
---

# AWS cloud threat model and accepted risks

## Goal
Update the architecture threat model for AWS trust boundaries, identity, data flows, and supply chain.

## Implementation subtasks
- [ ] Cover GitHub OIDC, Terraform state, AWS root/break-glass, EKS control plane, IRSA, ESO, Secrets Manager/KMS, ECR signatures, ALB, RDS, Redis, Amazon MQ, CloudTrail, GitOps repository and operator workstation
- [ ] model credential theft, malicious image, public exposure, lateral movement, data loss and supply-chain compromise
- [ ] assign mitigation owner and accepted-risk expiry.

## Acceptance criteria
- [ ] Threat diagram and abuse-case table cover every boundary and sensitive data class
- [ ] each high/critical risk has a control plus verification or an accepted owner/date
- [ ] residual risks and portfolio-only assumptions are distinguished from production requirements

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
