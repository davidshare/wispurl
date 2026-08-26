# Local Environment Checklist — DevOps / DevSecOps / SRE

Assumes: Docker, Docker Compose, a local GitLab CI runner or local Jenkins,
a local Kubernetes cluster (kind or k3d), Helm, and local ArgoCD for GitOps
deployment. Completed items are marked `[x]` in place, in their own
category — no separate "done" list.

---

## 1. Application Foundations
- [x] Docker Compose configuration for local development parity
- [ ] Dockerfiles for every service using multi-stage builds
- [ ] Separate configuration files for development, staging, and production environments
- [ ] Health endpoints: `/health`, `/ready`, and `/live`
- [ ] Graceful shutdown handling (SIGTERM) in application code
- [ ] Structured JSON logging with standardized fields
- [ ] Correlation/request IDs propagated across all service boundaries (via `contextvars`)
- [ ] API documentation generated and served via OpenAPI/Swagger
- [ ] Database migrations managed via Alembic (or Flyway/Liquibase)
- [ ] Seed data and repeatable local initialization scripts
- [ ] Strict dependency and version pinning (lockfiles)

## 2. Secrets Management (Local)
- [x] Gitleaks installed and actively scanning the repo for committed secrets
- [x] HashiCorp Vault deployed and running locally
- [ ] Vault initialized with a secure key-shares/unseal process documented (even in dev mode, document what production unseal would look like)
- [ ] Vault audit device enabled (logs every secret access)
- [ ] Vault policies defined per service/team (least privilege, not root-token-everywhere)
- [ ] Vault auth method configured for services (AppRole locally; Kubernetes auth once local k8s is up)
- [ ] Vault KV v2 secrets engine configured for application secrets
- [ ] Vault Database secrets engine configured for dynamic, short-lived DB credentials
- [ ] Vault Transit engine configured if any encryption-as-a-service need exists
- [ ] Vault PKI engine configured for internal TLS issuance (optional at local scale)
- [ ] Vault Agent or Agent Injector sidecar pattern tested locally
- [ ] Secret rotation process defined and tested at least once (manual is fine locally)
- [ ] Gitleaks wired in as a pre-commit hook, not just a manual/ad hoc scan
- [ ] Gitleaks added as a **blocking** CI pipeline stage (see Section 3)
- [ ] `.env` files git-ignored; `.env.example` maintained with placeholder values
- [ ] Verified no secrets get baked into Docker images (`docker history`, layer inspection)
- [ ] Documented process for developers to pull secrets from Vault rather than sharing via Slack/email
- [ ] Vault Raft snapshot backup configured (cross-ref Section 7)
- [ ] Vault snapshot restore drill executed at least once (cross-ref Section 7)

## 3. Testing
- [ ] Unit tests, run locally via Docker Compose
- [ ] Integration tests covering service interactions
- [ ] API/contract tests between services (e.g., Pact)
- [ ] Database migration tests verifying up/down scripts
- [ ] RabbitMQ and Redis integration tests using local containerized instances
- [ ] End-to-end (E2E) tests running against the local Kubernetes cluster
- [ ] Test coverage reporting integrated into local CI output
- [ ] Failure and timeout tests validating application resilience
- [ ] Local load testing scripts using k6 or Locust

## 4. Local CI/CD Pipeline (GitLab CI or Jenkins)
- [ ] Local GitLab CI runner registered, or local Jenkins instance/agent configured
- [ ] Pipeline stage: linting and code formatting
- [ ] Pipeline stage: static type checking
- [ ] Pipeline stage: unit and integration test execution
- [ ] Pipeline stage: secret scanning (Gitleaks) — **blocking**
- [ ] Pipeline stage: SAST with Semgrep and Bandit (Python)
- [ ] Pipeline stage: dependency vulnerability scanning (pip-audit, npm audit, etc.)
- [ ] Pipeline stage: filesystem/IaC scanning with Checkov
- [ ] Pipeline stage: container image build, tagged with Git commit SHA
- [ ] Pipeline stage: container image vulnerability scanning with Trivy
- [ ] Pipeline stage: SBOM generation with Syft
- [ ] Pipeline stage: push verified images to a local container registry (local Docker Registry or Harbor)
- [ ] Pipeline stage: trigger local ArgoCD sync / Helm upgrade against the local Kubernetes cluster
- [ ] Pipeline stage: post-deployment smoke tests against local Kubernetes

Pipeline shape to aim for:
```text
commit → lint → type check → test → secret scan (blocking)
       → SAST → dependency scan → IaC scan
       → build image → scan image → SBOM
       → push to local registry → ArgoCD sync
       → smoke test → rollback if unhealthy
```

## 5. Container Security (Local)
- [ ] Minimal base images (distroless, alpine)
- [ ] Containers run as non-root user
- [ ] Explicit `USER` instructions in all Dockerfiles
- [ ] Read-only root filesystems where application logic permits
- [ ] Unnecessary Linux capabilities dropped (Compose and Kubernetes manifests)
- [ ] CPU and memory limits defined in Compose and Kubernetes manifests
- [ ] Image versions pinned explicitly; no `latest` tag
- [ ] Local Kubernetes manifest scanning with Kubescape or KubeLinter

## 6. Observability (Local Stack)
- [ ] Prometheus deployed locally for metrics scraping
- [ ] Grafana deployed locally with pre-configured dashboards
- [ ] Application-level custom metrics exported
- [ ] Database metrics (PostgreSQL exporter) configured
- [ ] Redis metrics configured
- [ ] RabbitMQ metrics configured
- [ ] Node and container metrics via Node Exporter and cAdvisor
- [ ] Centralized log aggregation with Loki
- [ ] Log collection/forwarding via Grafana Alloy or Fluent Bit
- [ ] Distributed tracing implemented with OpenTelemetry
- [ ] Trace storage and visualization with Tempo or Jaeger
- [ ] Local Alertmanager configured with basic routing rules
- [ ] Dashboards covering RED metrics (Rate, Errors, Duration) and USE metrics (Utilization, Saturation, Errors)
- [ ] Runbook links attached to alert definitions (stubs are fine for now)

## 7. Reliability and SRE (Local Validation)
- [ ] Timeouts configured on every external network call
- [ ] Retries with exponential backoff implemented and tested
- [ ] Circuit breakers added for external dependencies
- [ ] Idempotency keys implemented for critical operations (payments, link creation)
- [ ] Rate limiting logic implemented and tested locally
- [ ] Dead-letter queues configured for failed message processing
- [ ] Health checks configured for all downstream dependencies
- [ ] Graceful degradation / fail-open / fail-closed behaviors documented and tested
- [ ] Chaos test: service restarts simulated and verified
- [ ] Chaos test: dependency failures simulated and verified
- [ ] Chaos test: message duplication simulated and verified
- [ ] Chaos test: database connection exhaustion simulated and verified
- [ ] Local rollback procedures tested and validated
- [ ] SLIs/SLOs/error budgets drafted (even provisionally) so cloud thresholds aren't invented from scratch later

## 8. Backups and Disaster Recovery (Local)
- [ ] PostgreSQL automated local backup scripts (`pg_dump`)
- [ ] PostgreSQL local restore testing documented and executed
- [ ] HashiCorp Vault Raft snapshots configured locally
- [ ] Vault snapshot restore testing executed
- [ ] Redis persistence strategy (RDB/AOF) decided and configured
- [ ] RabbitMQ definitions export/import drill
- [ ] Local disaster recovery procedure documented
- [ ] Draft RPO/RTO targets (to be formalized in the cloud environment)

Remember: **backup exists ≠ recovery is proven** — run the restore, don't just take the backup.

## 9. Local Kubernetes and Packaging
- [ ] Local Kubernetes cluster provisioned (kind, k3d, or minikube)
- [ ] Helm charts created for all application services
- [ ] Helm values files separated for local, staging, and production
- [ ] Kustomize overlays or Helm environment management configured
- [ ] Local ArgoCD deployed and configured for GitOps synchronization
- [ ] Kubernetes Namespaces defined and utilized
- [ ] Kubernetes Deployments, Services, and ConfigMaps defined
- [ ] Local secret management integrated with local Vault (via External Secrets Operator) or Kubernetes Secrets — see Section 2 for the Vault side of this
- [ ] ServiceAccounts and local RBAC policies defined
- [ ] Resource requests and limits explicitly defined for all pods
- [ ] Liveness, Readiness, and Startup probes configured
- [ ] Horizontal Pod Autoscaler configured (requires local metrics-server)
- [ ] Pod Disruption Budgets defined
- [ ] Default-deny NetworkPolicies applied
- [ ] Local Ingress configured (e.g., ingress-nginx)
- [ ] Local TLS certificates generated (e.g., via mkcert)
- [ ] PersistentVolumes and PersistentVolumeClaims defined for stateful components
- [ ] Jobs and CronJobs configured for background tasks
- [ ] StatefulSets used for stateful components if not using external containers
- [ ] Pod Security Standards (Restricted) enforced
- [ ] Local Kubernetes audit logging enabled

## 10. Security and Compliance (Local)
- [ ] RBAC and least privilege enforced in local cluster
- [ ] Network segmentation / default-deny NetworkPolicies applied
- [ ] TLS used locally wherever practical
- [ ] Threat model drafted for the application architecture
- [ ] Documented security assumptions

## 11. Operations and Incident Response (Local)
- [ ] Common local troubleshooting commands documented
- [ ] Local deployment runbook created
- [ ] Local rollback runbook created
- [ ] Local database recovery runbook created
- [ ] Local Vault recovery runbook created
- [ ] Local RabbitMQ recovery runbook created

## 12. Cost and Capacity Management (Local)
- [ ] Resource requests/limits strictly defined to prevent local resource starvation
- [ ] Local load and capacity tests executed to establish baseline performance
- [ ] Local log and metric retention limits configured to prevent disk exhaustion

---

## Suggested build order (local)

1. Application foundations + tests + structured logging
2. Harden secrets management (Vault policies, auth methods, rotation, blocking Gitleaks gate)
3. Local observability stack (Prometheus, Grafana, Loki, Tempo, Alertmanager)
4. Secure CI/CD pipeline (GitLab CI or Jenkins, all scanning stages)
5. Local Kubernetes (kind/k3d) + Helm + ArgoCD GitOps loop
6. Reliability/chaos drills + backup & restore drills
7. Runbooks and operational documentation