# Local DevOps, DevSecOps, and SRE Epic

## Goal

Build a complete local production-style delivery and operations system for WispURL: reproducible application foundations, preventive security, automated CI/CD, Kubernetes and GitOps, observability, and tested reliability and recovery practices. AWS and cloud delivery are tracked separately and are outside this local epic.

## How to use this epic

- Implement issues in the phase order below. Later work may proceed in parallel only when its listed prerequisites are complete.
- Epic checkboxes track whole-issue completion. Check one only after that issue’s acceptance criteria and verification evidence are complete.
- Stable issue IDs (`local-NNN`) remain in each issue’s frontmatter and in `depends_on`; filenames and folders are organizational only.
- The `Status` shown below is the issue frontmatter status at the time this epic was created; update it when the issue status changes.

## Ordered implementation plan

### 1. Establish project and application foundations

- [ ] **01.** [local-038: Local threat model and security assumptions](security/security-00-local-threat-model-and-security-assumptions.md) — status: `not_started`; depends on: `[]`
- [ ] **02.** [local-003: Environment configuration and safe local examples](docker/docker-00-environment-configuration-and-safe-local-examples.md) — status: `not_started`; depends on: `[]`
- [ ] **03.** [local-006: Dependency lockfiles and reproducible installs](app/app-00-dependency-lockfiles-and-reproducible-installs.md) — status: `not_started`; depends on: `[]`
- [ ] **04.** [local-002: Multi-stage application images and runtime hardening](containers/container-00-multi-stage-application-images-and-runtime-hardening.md) — status: `not_started`; depends on: `[]`
- [ ] **05.** [local-001: Docker Compose local stack baseline](docker/docker-01-docker-compose-local-stack-baseline.md) — status: `verify`; depends on: `[]`
- [ ] **06.** [local-005: Database migrations and repeatable seed data](app/app-01-database-migrations-and-repeatable-seed-data.md) — status: `not_started`; depends on: `[]`
- [ ] **07.** [local-004: Service health, shutdown, logging, and request correlation](app/app-02-service-health-shutdown-logging-and-request-correlation.md) — status: `not_started`; depends on: `[]`
- [ ] **08.** [local-026: Local application test suite and coverage](app/app-03-local-application-test-suite-and-coverage.md) — status: `not_started`; depends on: `[]`

### 2. Establish developer and runtime security

- [ ] **09.** [local-009: Gitleaks developer installation, policy, and pre-commit gate](security/security-01-gitleaks-developer-installation-policy-and-pre-commit-gate.md) — status: `not_started`; depends on: `[]`
- [ ] **10.** [local-007: Local Vault deployment, engines, identity, and lifecycle](security/security-02-local-vault-deployment-engines-identity-and-lifecycle.md) — status: `verify`; depends on: `[]`
- [ ] **11.** [local-008: Application services authenticate to Vault and consume scoped secrets](security/security-03-application-services-authenticate-to-vault-and-consume-scoped-secrets.md) — status: `not_started`; depends on: `[local-007]`

### 3. Build the delivery pipeline and security gates

- [ ] **12.** [local-010: GitHub Actions continuous integration pipeline](cicd/cicd-00-github-actions-continuous-integration-pipeline.md) — status: `not_started`; depends on: `[]`
- [ ] **13.** [local-011: Blocking Gitleaks CI gate](security/security-04-blocking-gitleaks-ci-gate.md) — status: `not_started`; depends on: `[local-010]`
- [ ] **14.** [local-012: Static analysis and dependency vulnerability gates](security/security-05-static-analysis-and-dependency-vulnerability-gates.md) — status: `not_started`; depends on: `[local-010]`
- [ ] **15.** [local-013: Checkov infrastructure and configuration gate](security/security-06-checkov-infrastructure-and-configuration-gate.md) — status: `not_started`; depends on: `[local-010]`
- [ ] **16.** [local-014: Container build, Trivy scan, and local registry publishing](containers/container-01-container-build-trivy-scan-and-local-registry-publishing.md) — status: `not_started`; depends on: `[local-010]`
- [ ] **17.** [local-015: Syft SBOM generation and artifact retention](cicd/cicd-01-syft-sbom-generation-and-artifact-retention.md) — status: `not_started`; depends on: `[local-010, local-014]`

### 4. Deliver local observability

- [ ] **18.** [local-020: Prometheus metrics collection and exporters](observability/obs-00-prometheus-metrics-collection-and-exporters.md) — status: `not_started`; depends on: `[]`
- [ ] **19.** [local-022: Centralized logs with Loki and Alloy](observability/obs-01-centralized-logs-with-loki-and-alloy.md) — status: `not_started`; depends on: `[]`
- [ ] **20.** [local-023: Tempo trace storage and query backend](observability/obs-02-tempo-trace-storage-and-query-backend.md) — status: `not_started`; depends on: `[]`
- [ ] **21.** [local-024: OpenTelemetry instrumentation in WispURL services](observability/obs-03-opentelemetry-instrumentation-in-wispurl-services.md) — status: `not_started`; depends on: `[local-020, local-022, local-023]`
- [ ] **22.** [local-021: Grafana dashboards and data sources](observability/obs-04-grafana-dashboards-and-data-sources.md) — status: `not_started`; depends on: `[local-020]`
- [ ] **23.** [local-025: Local Alertmanager rules and runbook links](observability/obs-05-local-alertmanager-rules-and-runbook-links.md) — status: `not_started`; depends on: `[local-020, local-021]`

### 5. Add the local Kubernetes and GitOps platform

- [ ] **24.** [local-016: Kind local Kubernetes cluster and security baseline](kubernetes/k8s-00-kind-local-kubernetes-cluster-and-security-baseline.md) — status: `not_started`; depends on: `[]`
- [ ] **25.** [local-017: Helm packaging for WispURL workloads](kubernetes/k8s-01-helm-packaging-for-wispurl-workloads.md) — status: `not_started`; depends on: `[local-016]`
- [ ] **26.** [local-034: Kind manifests and workload security controls](kubernetes/k8s-02-kind-manifests-and-workload-security-controls.md) — status: `not_started`; depends on: `[local-016, local-017]`
- [ ] **27.** [local-035: Kubernetes manifest security scanning](security/security-08-kubernetes-manifest-security-scanning.md) — status: `not_started`; depends on: `[local-010, local-017]`
- [ ] **28.** [local-018: ArgoCD local GitOps deployment](kubernetes/k8s-03-argocd-local-gitops-deployment.md) — status: `not_started`; depends on: `[local-016, local-017]`
- [ ] **29.** [local-019: Local Vault secrets integration with Kubernetes](security/security-07-local-vault-secrets-integration-with-kubernetes.md) — status: `not_started`; depends on: `[local-007, local-016, local-017]`
- [ ] **30.** [local-027: Local Kubernetes E2E tests and smoke checks](kubernetes/k8s-04-local-kubernetes-e2e-tests-and-smoke-checks.md) — status: `not_started`; depends on: `[local-016, local-017, local-018]`

### 6. Add reliability controls, recovery, and operational practice

- [ ] **31.** [local-028: Resilience controls for outbound calls and message processing](app/app-04-resilience-controls-for-outbound-calls-and-message-processing.md) — status: `not_started`; depends on: `[]`
- [ ] **32.** [local-029: RabbitMQ dead-lettering and duplicate-delivery safety](app/app-05-rabbitmq-dead-lettering-and-duplicate-delivery-safety.md) — status: `not_started`; depends on: `[local-028]`
- [ ] **33.** [local-031: Local database backup and restore](sre/sre-00-local-database-backup-and-restore.md) — status: `not_started`; depends on: `[]`
- [ ] **34.** [local-032: Redis and RabbitMQ persistence/recovery](sre/sre-01-redis-and-rabbitmq-persistence-recovery.md) — status: `not_started`; depends on: `[]`
- [ ] **35.** [local-033: SLIs, SLOs, error budgets, and local rollback policy](sre/sre-02-slis-slos-error-budgets-and-local-rollback-policy.md) — status: `not_started`; depends on: `[]`
- [ ] **36.** [local-030: Local failure injection and chaos validation](sre/sre-03-local-failure-injection-and-chaos-validation.md) — status: `not_started`; depends on: `[local-026, local-028]`
- [ ] **37.** [local-039: Local load and capacity baseline plus retention limits](sre/sre-04-local-load-and-capacity-baseline-plus-retention-limits.md) — status: `not_started`; depends on: `[local-020, local-021, local-031]`
- [ ] **38.** [local-036: PostgreSQL, Vault, and RabbitMQ recovery runbooks](sre/sre-05-postgresql-vault-and-rabbitmq-recovery-runbooks.md) — status: `not_started`; depends on: `[local-007, local-029, local-031]`
- [ ] **39.** [local-037: Local operational guide and troubleshooting](sre/sre-06-local-operational-guide-and-troubleshooting.md) — status: `not_started`; depends on: `[local-001, local-010]`

## Completion definition

The local epic is complete when every issue above is complete, all required acceptance criteria have evidence, and a contributor can reproduce the application and delivery workflow from a clean checkout. A running Compose stack alone does not complete the CI/CD, Kubernetes, security validation, or SRE drill issues.
