#!/usr/bin/env sh
set -eu

# Stateless; no database, no migrations. Just serve traffic.
exec gunicorn app.main:app \
  -k uvicorn.workers.UvicornWorker \
  --workers "${WEB_CONCURRENCY:-2}" \
  --bind "0.0.0.0:${PORT:-8000}"
