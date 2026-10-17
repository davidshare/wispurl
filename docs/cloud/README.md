# Cloud implementation issues

The [Cloud DevOps, DevSecOps, and SRE Epic](EPIC.md) is the canonical implementation order and whole-issue tracker. Confirmed choices are AWS, EKS, ArgoCD, AWS Secrets Manager, and GitHub Actions with OIDC. Terraform owns infrastructure; Ansible is excluded unless an uncovered configuration task requires it. Vault is not deployed in AWS: cloud secret requirements use AWS Secrets Manager equivalents or are marked not applicable with a reason. Issue IDs and dependency references are stable; filenames are grouped by engineering area.

## Issue directories

- [`foundation/`](./foundation/) — AWS account, Terraform state, and IaC ownership (3 issues)
- [`network/`](./network/) — VPC networking, ingress, DNS, and certificates (2 issues)
- [`security/`](./security/) — Secrets, workload identity, cluster controls, threat modeling, and security operations (5 issues)
- [`cicd/`](./cicd/) — GitHub Actions, secret scanning, and update automation (3 issues)
- [`supply-chain/`](./supply-chain/) — Production images, SBOM, signing, ECR, and admission verification (2 issues)
- [`kubernetes/`](./kubernetes/) — EKS, ArgoCD, workload packaging, deployment checks, and progressive delivery (5 issues)
- [`data/`](./data/) — RDS, ElastiCache, Amazon MQ, S3, backups, and managed-service integration (6 issues)
- [`observability/`](./observability/) — AWS metrics, logs, traces, alerts, and SLOs (2 issues)
- [`operations/`](./operations/) — Cost/capacity, resilience, load testing, ownership, DR, and recovery runbooks (6 issues)

Issue-level status and acceptance evidence remain in each issue file. Epic checkboxes represent whole-issue completion, not individual implementation subtasks. No issue is marked complete merely because the plan is documented.
