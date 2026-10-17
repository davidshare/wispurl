#!/usr/bin/env sh
set -eu

# Prometheus multiprocess mode: each Gunicorn worker writes its metrics to this
# directory and /metrics sums them. Start empty so a previous run isn't counted.
if [ -n "${PROMETHEUS_MULTIPROC_DIR:-}" ]; then
  rm -rf "$PROMETHEUS_MULTIPROC_DIR"
  mkdir -p "$PROMETHEUS_MULTIPROC_DIR"
fi

# The gateway is stateless (no database, no migrations); just serve traffic.
exec gunicorn app.main:app \
  -c python:wispurl_metrics.gunicorn_hooks \
  -k uvicorn.workers.UvicornWorker \
  --workers "${WEB_CONCURRENCY:-2}" \
  --bind "0.0.0.0:${PORT:-8000}"
