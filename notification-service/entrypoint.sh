#!/usr/bin/env sh
set -eu

# Queue-driven worker: no web server, no migrations. Consumes notifications.all.
exec python -m app.main
