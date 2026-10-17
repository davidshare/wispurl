# Runbooks

One page per alert in [`observability/prometheus/rules/wispurl-alerts.yml`](../../observability/prometheus/rules/wispurl-alerts.yml). Each alert's `runbook_url` points here.

| Alert | Severity |
| --- | --- |
| [TargetDown](target-down.md) | critical |
| [ServiceDisappeared](service-disappeared.md) | critical |
| [MetricsPipelineDown](metrics-pipeline-down.md) | critical |
| [HighErrorRate](high-error-rate.md) | warning |
| [HighLatencyP95](high-latency.md) | warning |
| [PostgresDown](postgres-down.md) | critical |
| [PostgresConnectionsHigh](postgres-connections-high.md) | warning |
| [RedisDown](redis-down.md) | critical |
| [DeadLetterQueueNotEmpty](dead-letter-queue-not-empty.md) | warning |
| [QueueBacklogGrowing](queue-backlog-growing.md) | warning |
| [HostDiskAlmostFull](host-disk-almost-full.md) | warning |
