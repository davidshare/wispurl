---
id: cloud-008
title: Amazon MQ RabbitMQ and message recovery
type: feat
feature: 9. Infrastructure as Code
status: not_started
depends_on: [cloud-001]
checklist_sections: 9. Infrastructure as Code; 8. Backups and Disaster Recovery
---

# Amazon MQ RabbitMQ and message recovery

## Goal
Provision a private managed RabbitMQ service and carry forward local durable queues, DLQ, and duplicate-delivery behavior.

## Implementation subtasks
- [ ] Select smallest supported broker topology meeting demonstrator goals
- [ ] restrict broker subnets and security groups to producer/consumer workloads
- [ ] store broker credentials in Secrets Manager
- [ ] configure TLS, durable exchanges/queues, dead-letter exchange, retry/TTL policy, alarms and maintenance
- [ ] define definitions/export or broker recovery limitations
- [ ] estimate always-on cost before creating.

## Acceptance criteria
- [ ] Only approved app identities connect over TLS
- [ ] credentials rotate without source change
- [ ] poison message reaches DLQ after bounded retry
- [ ] duplicate delivery has one logical side effect
- [ ] broker recovery/rebuild steps restore topology
- [ ] cost is documented and environment can be removed cleanly

## Verification evidence to attach
- [ ] Record the exact environment, tool versions, and commands or operator actions used.
- [ ] Attach successful output and the relevant failure/recovery scenario required above.
- [ ] Link dashboards, CI runs, scan reports, restore records, or rendered deployment state as applicable.
