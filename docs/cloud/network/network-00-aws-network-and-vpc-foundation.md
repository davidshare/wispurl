---
id: cloud-002
title: AWS network and VPC foundation
type: feat
feature: 9. Infrastructure as Code
status: not_started
depends_on: [cloud-001]
checklist_sections: 9. Infrastructure as Code
---

# AWS network and VPC foundation

## Goal
Build an EKS-ready VPC with explicit public/private boundaries and controlled outbound access.

## Implementation subtasks
- [ ] Create multi-AZ private subnets for EKS nodes and RDS/ElastiCache/Amazon MQ
- [ ] public subnets only for internet-facing ALB and NAT
- [ ] route tables and security groups use least privilege
- [ ] add VPC endpoints for S3, ECR, CloudWatch, Secrets Manager and STS where cost-effective
- [ ] document NAT/VPC endpoint monthly costs
- [ ] no database/broker public IPs.

## Acceptance criteria
- [ ] Terraform outputs show intended subnet roles across at least two AZs
- [ ] DB and broker have no public endpoint
- [ ] only ALB accepts public ingress
- [ ] EKS workloads can reach required AWS APIs
- [ ] security group review identifies no wildcard admin ports
- [ ] cost estimate includes NAT/endpoints

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
