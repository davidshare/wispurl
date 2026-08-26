# Cloud Environment Checklist — DevOps / DevSecOps / SRE

Translation of the proven local practices into a production-grade cloud
environment. Assumes Terraform, managed cloud services, a managed
Kubernetes service (AWS EKS / GCP GKE / Azure AKS), and cloud-native
security and observability integrations. Every category here mirrors a
category in the local checklist — nothing new is designed here, it's
ported and hardened.

---

## 1. Application Foundations (Cloud Optimization)
- [ ] Production-specific configuration management (env vars injected via External Secrets)
- [ ] Optimized production Docker images (stripped of debug tools and build dependencies)
- [ ] Production database connection pooling configured (e.g., PgBouncer)
- [ ] Production-grade CORS and security headers configured

## 2. Secrets Management (Cloud)
- [ ] Vault deployed in HA mode (Vault Enterprise/HCP Vault), or paired with/replaced by a cloud-native secret manager (AWS Secrets Manager, GCP Secret Manager)
- [ ] Vault storage backend durable and highly available (Integrated Storage/Raft cluster or Consul backend — not single-node dev mode)
- [ ] Vault auto-unseal configured (cloud KMS-backed) so restarts don't require manual unseal shares
- [ ] External Secrets Operator syncing Vault (or cloud secret manager) secrets into Kubernetes
- [ ] IAM Roles for Service Accounts (IRSA) or Workload Identity used instead of static cloud credentials anywhere possible
- [ ] Vault audit logging shipped to centralized, tamper-evident log storage
- [ ] Dynamic secrets used for databases (Vault DB secrets engine or equivalent) instead of long-lived static credentials
- [ ] Secret rotation automated for database credentials, API keys, and cloud access keys
- [ ] Vault PKI engine (or ACM/cert-manager) issuing short-lived internal TLS certs
- [ ] Vault DR: cross-region replication (Enterprise) or scheduled snapshot-based recovery plan for production
- [ ] Gitleaks (or equivalent) enforced as a **blocking** gate in cloud CI pipelines, not just local
- [ ] Secrets never appear in Terraform state in plaintext — `sensitive = true` on all secret outputs/variables, remote state encrypted at rest
- [ ] Cloud KMS used for encryption-at-rest of all secret stores and their backups
- [ ] Access to production secrets is logged and alertable (who read which secret, when)
- [ ] Break-glass procedure documented for emergency secret access outside normal auth flow
- [ ] Vault Raft/Consul snapshot backups scheduled to cloud object storage (cross-ref Section 7)
- [ ] Vault snapshot restore drill executed against a real recovery environment (cross-ref Section 7)

## 3. Testing (Cloud / Pre-Production)
- [ ] Staging environment E2E tests executed against cloud-like infrastructure
- [ ] Cloud integration tests validating managed service connectivity (RDS, ElastiCache, etc.)
- [ ] Production smoke tests executed immediately post-deployment
- [ ] Load testing re-run against real cloud infrastructure (not just local baselines)

## 4. Cloud CI/CD Pipeline (GitLab CI or Jenkins)
- [ ] Cloud-hosted GitLab CI runners or Jenkins agents with appropriate IAM permissions
- [ ] Separate pipeline definitions/workflows for development, staging, and production
- [ ] Manual deployment approval gates for staging and production
- [ ] Pipeline stage: image signing with Cosign
- [ ] Pipeline stage: SBOM attestation and storage
- [ ] Pipeline stage: push signed images to a cloud container registry (ECR, Artifact Registry, etc.)
- [ ] Pipeline stage: Terraform plan + security scanning (tfsec, Checkov) on infrastructure changes
- [ ] Pipeline stage: automated rollback triggers based on failed smoke tests/health checks
- [ ] Pipeline stage: GitOps repository update (e.g., ArgoCD Image Updater)

Pipeline shape:
```text
commit → lint → test → secret scan (blocking) → dependency scan
       → build image → scan image → SBOM → sign image (Cosign)
       → push to cloud registry → Terraform plan/apply (infra changes)
       → GitOps repo update → ArgoCD sync → smoke test
       → rollback if unhealthy
```

## 5. Container Security (Cloud)
- [ ] Admission controller (Kyverno or OPA Gatekeeper) verifying Cosign image signatures before deployment
- [ ] Admission controller enforcing Pod Security Standards (Restricted)
- [ ] Continuous container registry scanning enabled (ECR scanning, Trivy in CI)
- [ ] Automated dependency update process configured (Dependabot or Renovate)
- [ ] Runtime security monitoring configured (e.g., Falco)

## 6. Observability (Cloud Stack)
- [ ] Cloud-managed or highly-available Prometheus/VictoriaMetrics cluster
- [ ] Cloud-managed or highly-available Grafana instance with SSO/RBAC
- [ ] Cloud alert routing configured (Alertmanager → Slack, PagerDuty, Opsgenie, or email)
- [ ] Cloud-native log aggregation (Loki, CloudWatch Logs, or Datadog) with defined retention policies
- [ ] Distributed tracing backend scaled for production (managed Tempo, Jaeger, or cloud-native APM)
- [ ] SLOs and SLIs defined and monitored
- [ ] Error budgets defined, with alerting on burn rate
- [ ] Production dashboards: latency, traffic, errors, saturation, dependencies
- [ ] Runbooks explicitly linked from all production alerts

## 7. Reliability and SRE (Cloud)
- [ ] Multi-AZ deployment for all critical services
- [ ] Automated chaos engineering / failure injection scheduled (pod kills, node drains)
- [ ] Documented incident response procedures with defined severity levels
- [ ] Post-incident review (blameless retrospective) template established
- [ ] Change management process documented and enforced
- [ ] Maintenance window procedures defined
- [ ] Public or internal status page configured

## 8. Backups and Disaster Recovery (Cloud)
- [ ] PostgreSQL automated backups to object storage (S3) with continuous archiving (WAL-G)
- [ ] Cloud PostgreSQL restore testing executed and documented
- [ ] HashiCorp Vault automated snapshots to cloud object storage
- [ ] Vault snapshot restore testing executed and documented
- [ ] Managed message broker (RabbitMQ/Amazon MQ) backup or recovery strategy defined
- [ ] Cloud object storage (S3/GCS) configured for all backup artifacts
- [ ] Backup encryption at rest enabled (KMS)
- [ ] Backup retention policies enforced via lifecycle rules
- [ ] Recovery Point Objective (RPO) formally defined and met
- [ ] Recovery Time Objective (RTO) formally defined and met
- [ ] Documented, comprehensive disaster recovery procedure
- [ ] Periodic, scheduled disaster recovery drills executed

Remember: **backup exists ≠ recovery is proven** — schedule real restores, not just backup jobs.

## 9. Infrastructure as Code (Terraform + Ansible)
- [ ] Terraform configured with remote state backend (S3)
- [ ] State locking configured (DynamoDB)
- [ ] Terraform workspaces or directory structure separated by environment (dev/staging/production)
- [ ] VPC and networking infrastructure defined (public/private subnets, NAT Gateways, Internet Gateways)
- [ ] Route tables and VPC endpoints configured for secure internal traffic
- [ ] Security groups configured with least-privilege ingress/egress rules
- [ ] IAM roles and policies defined with strict least-privilege access
- [ ] Managed PostgreSQL (RDS/Cloud SQL) provisioned
- [ ] Managed Redis (ElastiCache/Memorystore) provisioned
- [ ] Managed RabbitMQ or equivalent message broker provisioned
- [ ] Cloud Load Balancer (ALB/NLB) provisioned and configured
- [ ] DNS management configured (Route 53/Cloud DNS)
- [ ] TLS certificates provisioned and managed (ACM or cert-manager)
- [ ] Cloud object storage buckets provisioned with versioning and encryption
- [ ] Cloud monitoring/alerting resources (CloudWatch alarms, budget alerts) defined in Terraform
- [ ] Ansible playbooks for any config-management tasks Terraform doesn't own

Suggested structure:
```text
infrastructure/
├── terraform/
│   ├── modules/
│   ├── environments/
│   │   ├── dev/
│   │   ├── staging/
│   │   └── production/
│   └── versions.tf
└── ansible/
```

## 10. Cloud Kubernetes and Packaging
- [ ] Managed Kubernetes cluster provisioned (EKS/GKE/AKS)
- [ ] Helm charts used for all application deployments
- [ ] GitOps repository established as the single source of truth for cluster state
- [ ] ArgoCD or Flux deployed and configured for continuous delivery
- [ ] Automatic image update strategy configured (ArgoCD Image Updater)
- [ ] Deployment history and rollback capabilities verified in GitOps tool
- [ ] Progressive delivery evaluated/implemented (canary or blue-green via Argo Rollouts)
- [ ] External Secrets Operator syncing secrets from Vault or cloud Secret Manager to Kubernetes — see Section 2
- [ ] IAM Roles for Service Accounts (IRSA) or Workload Identity configured for pod-level cloud permissions
- [ ] Cloud Load Balancer Controller configured for ingress traffic
- [ ] cert-manager configured for automated TLS provisioning and renewal
- [ ] Kubernetes audit logging enabled and shipped to a centralized logging backend

## 11. Security and Compliance (Cloud)
- [ ] Strict RBAC enforced; no cluster-admin bindings for applications
- [ ] Network segmentation via strict Kubernetes NetworkPolicies
- [ ] TLS enforced everywhere practical (service-to-service mTLS via mesh, or strict ingress TLS)
- [ ] Cloud audit logs (CloudTrail/GCP Audit Logs) enabled and monitored
- [ ] Documented security incident response procedure
- [ ] Formal threat model documented for the application architecture
- [ ] Documented security assumptions and accepted risks

## 12. Operations and Incident Response (Cloud)
- [ ] Clear service ownership assigned (team or individual)
- [ ] On-call/escalation process defined and tooling configured
- [ ] Cloud-specific deployment runbook created
- [ ] Cloud-specific rollback runbook created
- [ ] Cloud database recovery runbook created
- [ ] Cloud Vault recovery runbook created
- [ ] Cloud message broker recovery runbook created
- [ ] Incident severity levels defined
- [ ] Post-incident review template established

## 13. Cost and Capacity Management (Cloud)
- [ ] Cloud cost estimates documented prior to provisioning
- [ ] Cloud budget alerts configured (e.g., SNS at 50%/80%/100% of budget)
- [ ] Autoscaling strategy defined and tested (Cluster Autoscaler/Karpenter, HPA, VPA)
- [ ] Storage growth monitoring and alerting configured
- [ ] Database connection-pool limits defined and monitored
- [ ] Log retention limits enforced to control storage costs
- [ ] Metrics retention limits enforced to control storage costs
- [ ] Periodic right-sizing reviews scheduled and executed
- [ ] Cloud cost monitoring tooling implemented (Kubecost, Infracost, or cloud-native cost explorer)

---

## Suggested build order (cloud)

1. Terraform foundations — VPC, IAM, remote state
2. Secrets management hardening — HA Vault, auto-unseal, dynamic secrets, ESO wiring
3. Managed data services — RDS, ElastiCache, Amazon MQ, S3
4. EKS/GKE/AKS cluster + Helm charts ported from local + ArgoCD pointed at the real repo
5. Cloud CI/CD — signed images, admission control, approval gates
6. Cloud observability — same stack as local, now against real traffic, plus SLOs/error budgets
7. Backups, DR drills, security review, cost review — production-readiness pass