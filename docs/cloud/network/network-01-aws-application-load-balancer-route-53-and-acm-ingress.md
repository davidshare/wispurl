---
id: cloud-009
title: AWS Application Load Balancer, Route 53, and ACM ingress
type: feat
feature: 9. Infrastructure as Code
status: not_started
depends_on: [cloud-002, cloud-004]
checklist_sections: 9. Infrastructure as Code; 10. Cloud Kubernetes
---

# AWS Application Load Balancer, Route 53, and ACM ingress

## Goal
Expose only the gateway and frontend through a managed AWS ingress path.

## Implementation subtasks
- [ ] Install AWS Load Balancer Controller with IRSA
- [ ] provision ALB in public subnets and target workloads in private subnets
- [ ] use ACM-managed TLS, HTTPS redirect and modern security policy
- [ ] create Route 53 record only when a demonstrator domain is supplied
- [ ] define health checks and access logs
- [ ] keep admin, Vault and internal service routes private.

## Acceptance criteria
- [ ] External scan sees only HTTPS ingress
- [ ] certificate chain is trusted and renews through ACM
- [ ] HTTP redirects to HTTPS
- [ ] ALB health follows gateway readiness
- [ ] internal analytics/rate-limiter and admin ports are not routed
- [ ] Route 53/DNS teardown behavior documented

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
