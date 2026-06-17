# Cleanup Service

Schedule-driven (not an API). Periodically sweeps `short_db` for links whose
`expires_at` has passed and are still active, deactivates them in batches, and
publishes a `link.expired` event per deactivated link.

- **Idempotent:** only active, past-expiry rows are selected, so re-running the sweep
  is a no-op.
- **Direct DB access:** connects to `short_db` directly (it's a batch maintenance
  job, not request-path logic). The alternative — calling a Shortener internal
  endpoint — is documented in `app/db.py`.
- **Becomes a Kubernetes CronJob** in the DevOps phase (one sweep per invocation, no
  loop); the Compose container loops with a sleep only for local dev.

## Configuration

Env: `DATABASE_URL` (short_db), `RABBITMQ_URL`, `CLEANUP_INTERVAL_SECONDS`,
`BATCH_SIZE`, `LOG_LEVEL`.

## Develop

```bash
uv sync
uv run ruff check .
uv run mypy --strict .
```
