---
id: cloud-018
title: AWS observability: AMP, Managed Grafana, CloudWatch, X-Ray, and alerts
type: feat
feature: 6. Observability
status: not_started
depends_on: [cloud-001, cloud-004]
checklist_sections: 6. Observability
---

# AWS observability: AMP, Managed Grafana, CloudWatch, X-Ray, and alerts

## Goal
Port local telemetry concepts to managed AWS observability while retaining OpenTelemetry conventions.

## Implementation subtasks
- [ ] Use Amazon Managed Service for Prometheus for app/cluster metrics and Amazon Managed Grafana with SSO/RBAC
- [ ] export structured logs to CloudWatch with explicit retention
- [ ] use OpenTelemetry Collector and AWS X-Ray for traces
- [ ] define RED/USE dashboards for gateway, app services, RDS, ElastiCache, Amazon MQ and EKS
- [ ] set SNS alert routing for availability, latency, saturation, queue growth, DB connection pressure, failed backups, secret access anomaly and budget
- [ ] attach runbook URL to every alert
- [ ] define retention and monthly cost.

## Acceptance criteria
- [ ] A synthetic user journey is visible in metrics, logs and trace with shared trace ID
- [ ] Grafana access follows role assignments
- [ ] each alert fires and resolves in a controlled scenario
- [ ] logs/metrics retention is enforced
- [ ] runbook URLs resolve
- [ ] all managed telemetry resources have budget estimates

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
