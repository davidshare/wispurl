#!/usr/bin/env sh
set -eu

# Schedule-driven worker: no web server, no migrations. Runs the sweep loop.
exec python -m app.main
