---
id: LOC-8.05
title: "Redis persistence strategy (RDB/AOF) decided and configured"
category: "8. Backups and Disaster Recovery (Local)"
status: todo
related:
  - docs/local/sre/sre-01-redis-and-rabbitmq-persistence-recovery.md
---

# Redis persistence strategy (RDB/AOF) decided and configured

## What
Decide and configure Redis persistence (RDB, AOF or none) based on what Redis holds.

## Current state
Redis has no volume or persistence config, so all data is lost on restart. It holds only rate-limit counters today.

## Subtasks
- [ ] Document the decision (counters are ephemeral → none or RDB is acceptable)
- [ ] Configure it explicitly (e.g. `--appendonly yes` + volume, or `--save ""` with a comment)
- [ ] Test the restart behaviour matches the decision

## Acceptance criteria
- [ ] Decision recorded, and the restart behaviour verified
