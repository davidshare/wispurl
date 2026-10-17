#!/usr/bin/env bash
# Creates a least-privilege login for the PostgreSQL metrics exporter (Alloy).
# pg_monitor grants read access to statistics views and nothing else.
#
# Postgres runs this automatically only when its data volume is first created.
# For an existing volume, run it once by hand:
#   docker compose exec postgres bash /docker-entrypoint-initdb.d/create-monitoring-role.sh
set -euo pipefail

: "${POSTGRES_MONITOR_PASSWORD:?POSTGRES_MONITOR_PASSWORD must be set (see .env.example)}"

psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  --set monitor_password="$POSTGRES_MONITOR_PASSWORD" <<-'SQL'
  SELECT 'CREATE ROLE wispurl_monitor LOGIN'
  WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'wispurl_monitor')\gexec
  ALTER ROLE wispurl_monitor WITH LOGIN PASSWORD :'monitor_password' CONNECTION LIMIT 3;
  GRANT pg_monitor TO wispurl_monitor;
SQL
