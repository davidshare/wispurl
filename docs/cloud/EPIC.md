# Cloud DevOps, DevSecOps, and SRE Epic

## Goal

Deliver WispURL as an AWS portfolio demonstrator using production-style controls: governed AWS accounts and Terraform, secure networking and workload identity, EKS and ArgoCD, managed data services, automated signed delivery, observability, and tested reliability and recovery.

## How to use this epic

- Implement issues in the phase order below. Parallel work is appropriate only when all listed prerequisites are complete.
- Epic checkboxes track whole-issue completion. Check an issue only after its acceptance criteria and verification evidence are complete.
- Stable issue IDs (`cloud-NNN`) remain in issue frontmatter and `depends_on`; folder names and filenames are organizational only.
- The status shown is the issue frontmatter status when this epic was generated; update it when an issue status changes.
- Cloud-031 is ordered first because the threat model should guide infrastructure choices. Its former dependencies on already-built Secrets Manager, EKS, and observability were removed as backwards prerequisites.

## Ordered implementation plan

### 1. Establish cloud architecture, account, and infrastructure foundations

- [ ] **01.** [cloud-031: AWS cloud threat model and accepted risks](security/security-00-aws-cloud-threat-model-and-accepted-risks.md) — status: `not_started`; depends on: `[]`
- [ ] **02.** [cloud-001: AWS account foundation, Terraform state, and cost guardrails](foundation/foundation-00-aws-account-foundation-terraform-state-and-cost-guardrails.md) — status: `not_started`; depends on: `[]`
- [ ] **03.** [cloud-033: Terraform and Ansible ownership boundary](foundation/foundation-01-terraform-and-ansible-ownership-boundary.md) — status: `not_started`; depends on: `[cloud-001]`
- [ ] **04.** [cloud-014: Terraform AWS infrastructure modules and environment separation](foundation/foundation-02-terraform-aws-infrastructure-modules-and-environment-separation.md) — status: `not_started`; depends on: `[cloud-001]`
- [ ] **05.** [cloud-002: AWS network and VPC foundation](network/network-00-aws-network-and-vpc-foundation.md) — status: `not_started`; depends on: `[cloud-001]`
- [ ] **06.** [cloud-003: AWS Secrets Manager, rotation, and recovery policy](security/security-01-aws-secrets-manager-rotation-and-recovery-policy.md) — status: `not_started`; depends on: `[cloud-001]`
- [ ] **07.** [cloud-010: S3 backup and artifact buckets](data/data-03-s3-backup-and-artifact-buckets.md) — status: `not_started`; depends on: `[cloud-001]`

### 2. Establish cloud delivery identity and supply-chain controls

- [ ] **08.** [cloud-011: GitHub Actions AWS delivery pipeline with OIDC](cicd/cicd-00-github-actions-aws-delivery-pipeline-with-oidc.md) — status: `not_started`; depends on: `[cloud-001]`
- [ ] **09.** [cloud-012: Cloud Gitleaks gate and secret incident workflow](cicd/cicd-01-cloud-gitleaks-gate-and-secret-incident-workflow.md) — status: `not_started`; depends on: `[cloud-011]`
- [ ] **10.** [cloud-028: Dependabot dependency and workflow update automation](cicd/cicd-02-dependabot-dependency-and-workflow-update-automation.md) — status: `not_started`; depends on: `[cloud-011]`
- [ ] **11.** [cloud-027: Production-optimized AWS application images](supply-chain/supply-00-production-optimized-aws-application-images.md) — status: `not_started`; depends on: `[cloud-011]`

### 3. Provision the AWS platform and managed service foundations

- [ ] **12.** [cloud-004: Amazon EKS cluster and cluster access](kubernetes/k8s-00-amazon-eks-cluster-and-cluster-access.md) — status: `not_started`; depends on: `[cloud-001, cloud-002]`
- [ ] **13.** [cloud-006: Amazon RDS PostgreSQL for WispURL data](data/data-00-amazon-rds-postgresql-for-wispurl-data.md) — status: `not_started`; depends on: `[cloud-001, cloud-002]`
- [ ] **14.** [cloud-007: Amazon ElastiCache Redis for rate limiting](data/data-01-amazon-elasticache-redis-for-rate-limiting.md) — status: `not_started`; depends on: `[cloud-001, cloud-002]`
- [ ] **15.** [cloud-008: Amazon MQ RabbitMQ and message recovery](data/data-02-amazon-mq-rabbitmq-and-message-recovery.md) — status: `not_started`; depends on: `[cloud-001]`
- [ ] **16.** [cloud-005: AWS application workload identity and secret projection](security/security-02-aws-application-workload-identity-and-secret-projection.md) — status: `not_started`; depends on: `[cloud-003, cloud-004]`
- [ ] **17.** [cloud-018: AWS observability: AMP, Managed Grafana, CloudWatch, X-Ray, and alerts](observability/obs-00-aws-observability-amp-managed-grafana-cloudwatch-x-ray-and-alerts.md) — status: `not_started`; depends on: `[cloud-001, cloud-004]`
- [ ] **18.** [cloud-019: Cloud SLI/SLO and error-budget policy](observability/obs-01-cloud-sli-slo-and-error-budget-policy.md) — status: `not_started`; depends on: `[cloud-018]`
- [ ] **19.** [cloud-023: AWS cost and capacity controls](operations/ops-00-aws-cost-and-capacity-controls.md) — status: `not_started`; depends on: `[cloud-001, cloud-018]`

### 4. Secure and deploy workloads through EKS and GitOps

- [ ] **20.** [cloud-013: Cloud SBOM, image signing, ECR publication, and admission verification](supply-chain/supply-01-cloud-sbom-image-signing-ecr-publication-and-admission-verification.md) — status: `not_started`; depends on: `[cloud-004, cloud-011]`
- [ ] **21.** [cloud-015: ArgoCD GitOps deployment on EKS](kubernetes/k8s-01-argocd-gitops-deployment-on-eks.md) — status: `not_started`; depends on: `[cloud-004, cloud-014]`
- [ ] **22.** [cloud-016: AWS Helm charts and production configuration for application services](kubernetes/k8s-02-aws-helm-charts-and-production-configuration-for-application-services.md) — status: `not_started`; depends on: `[cloud-015]`
- [ ] **23.** [cloud-017: EKS network policy, RBAC, pod security, and runtime protection](security/security-04-eks-network-policy-rbac-pod-security-and-runtime-protection.md) — status: `not_started`; depends on: `[cloud-004, cloud-016]`
- [ ] **24.** [cloud-009: AWS Application Load Balancer, Route 53, and ACM ingress](network/network-01-aws-application-load-balancer-route-53-and-acm-ingress.md) — status: `not_started`; depends on: `[cloud-002, cloud-004]`
- [ ] **25.** [cloud-025: Cloud deployment smoke tests and rollback verification](kubernetes/k8s-03-cloud-deployment-smoke-tests-and-rollback-verification.md) — status: `not_started`; depends on: `[cloud-011, cloud-015, cloud-018]`
- [ ] **26.** [cloud-029: Argo Rollouts progressive delivery evaluation](kubernetes/k8s-04-argo-rollouts-progressive-delivery-evaluation.md) — status: `not_started`; depends on: `[cloud-015, cloud-018]`

### 5. Validate reliability, recovery, cost, and operations

- [ ] **27.** [cloud-020: AWS backup and recovery: RDS, Secrets Manager, S3, and Amazon MQ](data/data-04-aws-backup-and-recovery-rds-secrets-manager-s3-and-amazon-mq.md) — status: `not_started`; depends on: `[cloud-003, cloud-006, cloud-008, cloud-010]`
- [ ] **28.** [cloud-024: Cloud PostgreSQL connection management and managed-service integration tests](data/data-05-cloud-postgresql-connection-management-and-managed-service-integration-tests.md) — status: `not_started`; depends on: `[cloud-006, cloud-008]`
- [ ] **29.** [cloud-021: Cloud resilience, multi-AZ and failure injection](operations/ops-01-cloud-resilience-multi-az-and-failure-injection.md) — status: `not_started`; depends on: `[cloud-004, cloud-018]`
- [ ] **30.** [cloud-022: Cloud security incident and change-management runbooks](security/security-03-cloud-security-incident-and-change-management-runbooks.md) — status: `not_started`; depends on: `[cloud-003, cloud-018]`
- [ ] **31.** [cloud-030: Cloud load test and scaling baseline](operations/ops-02-cloud-load-test-and-scaling-baseline.md) — status: `not_started`; depends on: `[cloud-018, cloud-023]`
- [ ] **32.** [cloud-032: Cloud service ownership, status view, and response guide](operations/ops-03-cloud-service-ownership-status-view-and-response-guide.md) — status: `not_started`; depends on: `[cloud-018, cloud-022]`
- [ ] **33.** [cloud-026: Cloud disaster-recovery and RPO/RTO drill calendar](operations/ops-04-cloud-disaster-recovery-and-rpo-rto-drill-calendar.md) — status: `not_started`; depends on: `[cloud-020, cloud-022]`
- [ ] **34.** [cloud-034: AWS deployment, rollback, and managed-service recovery runbooks](operations/ops-05-aws-deployment-rollback-and-managed-service-recovery-runbooks.md) — status: `not_started`; depends on: `[cloud-003, cloud-006, cloud-008, cloud-015]`

## Completion definition

The cloud epic is complete when each issue is complete, all required acceptance criteria have evidence, and the AWS deployment can be reproduced and operated with the documented identity, security, observability, rollback, and recovery controls. Portfolio-only assumptions must remain explicit and must not be presented as production guarantees.
