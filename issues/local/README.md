# Local issues

One issue per item in [LOCAL_CHECKLIST.md](../../LOCAL_CHECKLIST.md), grouped by checklist category.
Each issue has a summary, current state, subtasks and acceptance criteria — tick boxes as work lands.

**Status rules:** `todo` = no subtasks done · `partial` = some done · `done` = all subtasks and acceptance criteria met.
When an issue becomes `done`, update its `status:` front matter and tick the matching line in `LOCAL_CHECKLIST.md`.

**Follow-ups** are defects or hardening found on work whose checklist item is already met. They don't change an issue's status, but they should be fixed. Issues with open follow-ups:

- [Vault auth method for services](secrets-management/06-vault-auth-method-for-services.md) — frontend holds Vault credentials it doesn't need
- [Developer secrets from Vault](secrets-management/17-developer-secrets-from-vault.md) — `make vault-env` not in README
- [PostgreSQL exporter](observability/04-postgres-exporter.md) — superuser DSN, needs a `pg_monitor` role
- [Loki log aggregation](observability/08-loki-log-aggregation.md) — `reject_old_samples` removed on branch
- [Alloy log collection](observability/09-alloy-log-collection.md) — broken healthcheck, no JSON parsing/redaction/multiline, socket risk undocumented

| Category | Done | Partial | Todo | Total |
| --- | --- | --- | --- | --- |
| 1. [Application Foundations](#1-application-foundations) | 7 | 3 | 1 | 11 |
| 2. [Secrets Management (Local)](#2-secrets-management-local) | 11 | 2 | 6 | 19 |
| 3. [Testing](#3-testing) | 0 | 0 | 9 | 9 |
| 4. [Local CI/CD Pipeline (GitLab CI or Jenkins)](#4-local-cicd-pipeline-gitlab-ci-or-jenkins) | 0 | 0 | 14 | 14 |
| 5. [Container Security (Local)](#5-container-security-local) | 3 | 0 | 5 | 8 |
| 6. [Observability (Local Stack)](#6-observability-local-stack) | 7 | 2 | 5 | 14 |
| 7. [Reliability and SRE (Local Validation)](#7-reliability-and-sre-local-validation) | 2 | 4 | 8 | 14 |
| 8. [Backups and Disaster Recovery (Local)](#8-backups-and-disaster-recovery-local) | 1 | 0 | 7 | 8 |
| 9. [Local Kubernetes and Packaging](#9-local-kubernetes-and-packaging) | 0 | 0 | 21 | 21 |
| 10. [Security and Compliance (Local)](#10-security-and-compliance-local) | 0 | 1 | 4 | 5 |
| 11. [Operations and Incident Response (Local)](#11-operations-and-incident-response-local) | 0 | 1 | 5 | 6 |
| 12. [Cost and Capacity Management (Local)](#12-cost-and-capacity-management-local) | 0 | 1 | 2 | 3 |
| **Total** | **31** | **14** | **87** | **132** |

## 1. Application Foundations

- [x] [Docker Compose configuration for local development parity](application-foundations/01-docker-compose-local-parity.md)
- [x] [Dockerfiles for every service using multi-stage builds](application-foundations/02-multi-stage-dockerfiles.md)
- [ ] [Separate configuration files for development, staging, and production environments](application-foundations/03-environment-config-files.md)
- [ ] [Health endpoints: /health, /ready, and /live](application-foundations/04-health-ready-live-endpoints.md) _(partial)_
- [ ] [Graceful shutdown handling (SIGTERM) in application code](application-foundations/05-graceful-shutdown.md) _(partial)_
- [x] [Structured JSON logging with standardized fields](application-foundations/06-structured-json-logging.md)
- [x] [Correlation/request IDs propagated across all service boundaries (via contextvars)](application-foundations/07-correlation-request-ids.md)
- [x] [API documentation generated and served via OpenAPI/Swagger](application-foundations/08-openapi-documentation.md)
- [x] [Database migrations managed via Alembic (or Flyway/Liquibase)](application-foundations/09-alembic-migrations.md)
- [ ] [Seed data and repeatable local initialization scripts](application-foundations/10-seed-data-and-init-scripts.md) _(partial)_
- [x] [Strict dependency and version pinning (lockfiles)](application-foundations/11-dependency-lockfiles.md)

## 2. Secrets Management (Local)

- [x] [Gitleaks installed and actively scanning the repo for committed secrets](secrets-management/01-gitleaks-installed-and-scanning.md)
- [x] [HashiCorp Vault deployed and running locally](secrets-management/02-vault-deployed-locally.md)
- [x] [Vault initialized with a secure key-shares/unseal process documented (even in dev mode, document what production unseal would look like)](secrets-management/03-vault-init-and-unseal-process.md)
- [x] [Vault audit device enabled (logs every secret access)](secrets-management/04-vault-audit-device.md)
- [x] [Vault policies defined per service/team (least privilege, not root-token-everywhere)](secrets-management/05-vault-policies-per-service.md)
- [x] [Vault auth method configured for services (AppRole locally; Kubernetes auth once local k8s is up)](secrets-management/06-vault-auth-method-for-services.md)
- [x] [Vault KV v2 secrets engine configured for application secrets](secrets-management/07-vault-kv-v2.md)
- [ ] [Vault Database secrets engine configured for dynamic, short-lived DB credentials](secrets-management/08-vault-database-secrets-engine.md)
- [ ] [Vault Transit engine configured if any encryption-as-a-service need exists](secrets-management/09-vault-transit-engine.md)
- [ ] [Vault PKI engine configured for internal TLS issuance (optional at local scale)](secrets-management/10-vault-pki-engine.md)
- [ ] [Vault Agent or Agent Injector sidecar pattern tested locally](secrets-management/11-vault-agent-sidecar.md)
- [ ] [Secret rotation process defined and tested at least once (manual is fine locally)](secrets-management/12-secret-rotation.md)
- [x] [Gitleaks wired in as a pre-commit hook, not just a manual/ad hoc scan](secrets-management/13-gitleaks-pre-commit-hook.md)
- [ ] [Gitleaks added as a blocking CI pipeline stage (see Section 3)](secrets-management/14-gitleaks-blocking-ci.md) _(partial)_
- [x] [.env files git-ignored; .env.example maintained with placeholder values](secrets-management/15-env-files-gitignored.md)
- [ ] [Verified no secrets get baked into Docker images (docker history, layer inspection)](secrets-management/16-no-secrets-in-images.md) _(partial)_
- [x] [Documented process for developers to pull secrets from Vault rather than sharing via Slack/email](secrets-management/17-developer-secrets-from-vault.md)
- [x] [Vault Raft snapshot backup configured (cross-ref Section 7)](secrets-management/18-vault-raft-snapshot-backup.md)
- [ ] [Vault snapshot restore drill executed at least once (cross-ref Section 7)](secrets-management/19-vault-snapshot-restore-drill.md)

## 3. Testing

- [ ] [Unit tests, run locally via Docker Compose](testing/01-unit-tests.md)
- [ ] [Integration tests covering service interactions](testing/02-integration-tests.md)
- [ ] [API/contract tests between services (e.g., Pact)](testing/03-contract-tests.md)
- [ ] [Database migration tests verifying up/down scripts](testing/04-migration-tests.md)
- [ ] [RabbitMQ and Redis integration tests using local containerized instances](testing/05-rabbitmq-redis-integration-tests.md)
- [ ] [End-to-end (E2E) tests running against the local Kubernetes cluster](testing/06-e2e-tests-kubernetes.md)
- [ ] [Test coverage reporting integrated into local CI output](testing/07-coverage-reporting.md)
- [ ] [Failure and timeout tests validating application resilience](testing/08-failure-and-timeout-tests.md)
- [ ] [Local load testing scripts using k6 or Locust](testing/09-load-testing-scripts.md)

## 4. Local CI/CD Pipeline (GitLab CI or Jenkins)

- [ ] [Local GitLab CI runner registered, or local Jenkins instance/agent configured](ci-cd-pipeline/01-ci-runner.md)
- [ ] [Pipeline stage: linting and code formatting](ci-cd-pipeline/02-lint-and-format-stage.md)
- [ ] [Pipeline stage: static type checking](ci-cd-pipeline/03-type-check-stage.md)
- [ ] [Pipeline stage: unit and integration test execution](ci-cd-pipeline/04-test-stage.md)
- [ ] [Pipeline stage: secret scanning (Gitleaks) — blocking](ci-cd-pipeline/05-secret-scan-stage.md)
- [ ] [Pipeline stage: SAST with Semgrep and Bandit (Python)](ci-cd-pipeline/06-sast-stage.md)
- [ ] [Pipeline stage: dependency vulnerability scanning (pip-audit, npm audit, etc.)](ci-cd-pipeline/07-dependency-scan-stage.md)
- [ ] [Pipeline stage: filesystem/IaC scanning with Checkov](ci-cd-pipeline/08-checkov-iac-scan-stage.md)
- [ ] [Pipeline stage: container image build, tagged with Git commit SHA](ci-cd-pipeline/09-image-build-stage.md)
- [ ] [Pipeline stage: container image vulnerability scanning with Trivy](ci-cd-pipeline/10-trivy-image-scan-stage.md)
- [ ] [Pipeline stage: SBOM generation with Syft](ci-cd-pipeline/11-syft-sbom-stage.md)
- [ ] [Pipeline stage: push verified images to a local container registry (local Docker Registry or Harbor)](ci-cd-pipeline/12-push-to-local-registry.md)
- [ ] [Pipeline stage: trigger local ArgoCD sync / Helm upgrade against the local Kubernetes cluster](ci-cd-pipeline/13-argocd-sync-stage.md)
- [ ] [Pipeline stage: post-deployment smoke tests against local Kubernetes](ci-cd-pipeline/14-post-deploy-smoke-tests.md)

## 5. Container Security (Local)

- [x] [Minimal base images (distroless, alpine)](container-security/01-minimal-base-images.md)
- [x] [Containers run as non-root user](container-security/02-non-root-containers.md)
- [x] [Explicit USER instructions in all Dockerfiles](container-security/03-explicit-user-instructions.md)
- [ ] [Read-only root filesystems where application logic permits](container-security/04-read-only-root-filesystem.md)
- [ ] [Unnecessary Linux capabilities dropped (Compose and Kubernetes manifests)](container-security/05-drop-linux-capabilities.md)
- [ ] [CPU and memory limits defined in Compose and Kubernetes manifests](container-security/06-cpu-memory-limits.md)
- [ ] [Image versions pinned explicitly; no latest tag](container-security/07-pin-image-versions.md)
- [ ] [Local Kubernetes manifest scanning with Kubescape or KubeLinter](container-security/08-k8s-manifest-scanning.md)

## 6. Observability (Local Stack)

- [x] [Prometheus deployed locally for metrics scraping](observability/01-prometheus.md)
- [ ] [Grafana deployed locally with pre-configured dashboards](observability/02-grafana-with-dashboards.md)
- [x] [Application-level custom metrics exported](observability/03-application-custom-metrics.md)
- [x] [Database metrics (PostgreSQL exporter) configured](observability/04-postgres-exporter.md)
- [x] [Redis metrics configured](observability/05-redis-metrics.md)
- [x] [RabbitMQ metrics configured](observability/06-rabbitmq-metrics.md)
- [ ] [Node and container metrics via Node Exporter and cAdvisor](observability/07-node-and-container-metrics.md)
- [x] [Centralized log aggregation with Loki](observability/08-loki-log-aggregation.md)
- [x] [Log collection/forwarding via Grafana Alloy or Fluent Bit](observability/09-alloy-log-collection.md)
- [ ] [Distributed tracing implemented with OpenTelemetry](observability/10-opentelemetry-tracing.md) _(partial)_
- [ ] [Trace storage and visualization with Tempo or Jaeger](observability/11-tempo-trace-storage.md) _(partial)_
- [ ] [Local Alertmanager configured with basic routing rules](observability/12-alertmanager.md)
- [ ] [Dashboards covering RED metrics (Rate, Errors, Duration) and USE metrics (Utilization, Saturation, Errors)](observability/13-red-use-dashboards.md)
- [ ] [Runbook links attached to alert definitions (stubs are fine for now)](observability/14-alert-runbook-links.md)

## 7. Reliability and SRE (Local Validation)

- [ ] [Timeouts configured on every external network call](reliability-sre/01-timeouts-on-external-calls.md) _(partial)_
- [ ] [Retries with exponential backoff implemented and tested](reliability-sre/02-retries-with-backoff.md) _(partial)_
- [ ] [Circuit breakers added for external dependencies](reliability-sre/03-circuit-breakers.md)
- [ ] [Idempotency keys implemented for critical operations (payments, link creation)](reliability-sre/04-idempotency-keys.md)
- [ ] [Rate limiting logic implemented and tested locally](reliability-sre/05-rate-limiting.md) _(partial)_
- [x] [Dead-letter queues configured for failed message processing](reliability-sre/06-dead-letter-queues.md)
- [x] [Health checks configured for all downstream dependencies](reliability-sre/07-dependency-health-checks.md)
- [ ] [Graceful degradation / fail-open / fail-closed behaviors documented and tested](reliability-sre/08-graceful-degradation-matrix.md) _(partial)_
- [ ] [Chaos test: service restarts simulated and verified](reliability-sre/09-chaos-service-restarts.md)
- [ ] [Chaos test: dependency failures simulated and verified](reliability-sre/10-chaos-dependency-failures.md)
- [ ] [Chaos test: message duplication simulated and verified](reliability-sre/11-chaos-message-duplication.md)
- [ ] [Chaos test: database connection exhaustion simulated and verified](reliability-sre/12-chaos-db-connection-exhaustion.md)
- [ ] [Local rollback procedures tested and validated](reliability-sre/13-rollback-procedures-tested.md)
- [ ] [SLIs/SLOs/error budgets drafted (even provisionally) so cloud thresholds aren't invented from scratch later](reliability-sre/14-slis-slos-error-budgets.md)

## 8. Backups and Disaster Recovery (Local)

- [ ] [PostgreSQL automated local backup scripts (pg_dump)](backups-disaster-recovery/01-postgres-backup-scripts.md)
- [ ] [PostgreSQL local restore testing documented and executed](backups-disaster-recovery/02-postgres-restore-testing.md)
- [x] [HashiCorp Vault Raft snapshots configured locally](backups-disaster-recovery/03-vault-raft-snapshots.md)
- [ ] [Vault snapshot restore testing executed](backups-disaster-recovery/04-vault-snapshot-restore-testing.md)
- [ ] [Redis persistence strategy (RDB/AOF) decided and configured](backups-disaster-recovery/05-redis-persistence-strategy.md)
- [ ] [RabbitMQ definitions export/import drill](backups-disaster-recovery/06-rabbitmq-definitions-export-import.md)
- [ ] [Local disaster recovery procedure documented](backups-disaster-recovery/07-local-dr-procedure.md)
- [ ] [Draft RPO/RTO targets (to be formalized in the cloud environment)](backups-disaster-recovery/08-rpo-rto-targets.md)

## 9. Local Kubernetes and Packaging

- [ ] [Local Kubernetes cluster provisioned (kind, k3d, or minikube)](kubernetes-packaging/01-local-cluster.md)
- [ ] [Helm charts created for all application services](kubernetes-packaging/02-helm-charts.md)
- [ ] [Helm values files separated for local, staging, and production](kubernetes-packaging/03-helm-values-per-environment.md)
- [ ] [Kustomize overlays or Helm environment management configured](kubernetes-packaging/04-environment-management.md)
- [ ] [Local ArgoCD deployed and configured for GitOps synchronization](kubernetes-packaging/05-argocd-gitops.md)
- [ ] [Kubernetes Namespaces defined and utilized](kubernetes-packaging/06-namespaces.md)
- [ ] [Kubernetes Deployments, Services, and ConfigMaps defined](kubernetes-packaging/07-deployments-services-configmaps.md)
- [ ] [Local secret management integrated with local Vault (via External Secrets Operator) or Kubernetes Secrets — see Section 2 for the Vault side of this](kubernetes-packaging/08-vault-secrets-integration.md)
- [ ] [ServiceAccounts and local RBAC policies defined](kubernetes-packaging/09-serviceaccounts-rbac.md)
- [ ] [Resource requests and limits explicitly defined for all pods](kubernetes-packaging/10-resource-requests-limits.md)
- [ ] [Liveness, Readiness, and Startup probes configured](kubernetes-packaging/11-probes.md)
- [ ] [Horizontal Pod Autoscaler configured (requires local metrics-server)](kubernetes-packaging/12-horizontal-pod-autoscaler.md)
- [ ] [Pod Disruption Budgets defined](kubernetes-packaging/13-pod-disruption-budgets.md)
- [ ] [Default-deny NetworkPolicies applied](kubernetes-packaging/14-default-deny-network-policies.md)
- [ ] [Local Ingress configured (e.g., ingress-nginx)](kubernetes-packaging/15-local-ingress.md)
- [ ] [Local TLS certificates generated (e.g., via mkcert)](kubernetes-packaging/16-local-tls-certificates.md)
- [ ] [PersistentVolumes and PersistentVolumeClaims defined for stateful components](kubernetes-packaging/17-persistent-volumes.md)
- [ ] [Jobs and CronJobs configured for background tasks](kubernetes-packaging/18-jobs-and-cronjobs.md)
- [ ] [StatefulSets used for stateful components if not using external containers](kubernetes-packaging/19-statefulsets.md)
- [ ] [Pod Security Standards (Restricted) enforced](kubernetes-packaging/20-pod-security-standards.md)
- [ ] [Local Kubernetes audit logging enabled](kubernetes-packaging/21-kubernetes-audit-logging.md)

## 10. Security and Compliance (Local)

- [ ] [RBAC and least privilege enforced in local cluster](security-compliance/01-rbac-least-privilege.md)
- [ ] [Network segmentation / default-deny NetworkPolicies applied](security-compliance/02-network-segmentation.md)
- [ ] [TLS used locally wherever practical](security-compliance/03-local-tls.md) _(partial)_
- [ ] [Threat model drafted for the application architecture](security-compliance/04-threat-model.md)
- [ ] [Documented security assumptions](security-compliance/05-security-assumptions.md)

## 11. Operations and Incident Response (Local)

- [ ] [Common local troubleshooting commands documented](operations-incident-response/01-troubleshooting-commands.md) _(partial)_
- [ ] [Local deployment runbook created](operations-incident-response/02-deployment-runbook.md)
- [ ] [Local rollback runbook created](operations-incident-response/03-rollback-runbook.md)
- [ ] [Local database recovery runbook created](operations-incident-response/04-database-recovery-runbook.md)
- [ ] [Local Vault recovery runbook created](operations-incident-response/05-vault-recovery-runbook.md)
- [ ] [Local RabbitMQ recovery runbook created](operations-incident-response/06-rabbitmq-recovery-runbook.md)

## 12. Cost and Capacity Management (Local)

- [ ] [Resource requests/limits strictly defined to prevent local resource starvation](cost-capacity/01-resource-limits-budget.md)
- [ ] [Local load and capacity tests executed to establish baseline performance](cost-capacity/02-load-capacity-baseline.md)
- [ ] [Local log and metric retention limits configured to prevent disk exhaustion](cost-capacity/03-retention-limits.md) _(partial)_
