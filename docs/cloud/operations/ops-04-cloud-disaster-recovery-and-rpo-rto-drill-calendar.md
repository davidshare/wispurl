---
id: cloud-026
title: Cloud disaster-recovery and RPO/RTO drill calendar
type: feat
feature: 8. Backups and Disaster Recovery
status: not_started
depends_on: [cloud-020, cloud-022]
checklist_sections: 8. Backups and Disaster Recovery; 12. Operations
---

# Cloud disaster-recovery and RPO/RTO drill calendar

## Goal
Set service-specific recovery objectives and schedule recurring end-to-end restore drills.

## Implementation subtasks
- [ ] Set RPO/RTO for RDS, Secrets Manager, S3 artifacts, RabbitMQ topology/messages and EKS/GitOps reconstruction
- [ ] include cross-region plan only where portfolio budget permits
- [ ] create quarterly drill calendar
- [ ] test infrastructure recreation from Terraform and ArgoCD from Git
- [ ] record measured recovery and data loss
- [ ] update objectives when measured results miss target.

## Acceptance criteria
- [ ] Each data class has a justified RPO/RTO
- [ ] a scheduled full-stack recovery exercise recreates infrastructure, secrets access and deployment from source of truth
- [ ] measured values are compared against objectives
- [ ] gaps have tracked remediation and date

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
