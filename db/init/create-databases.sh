#!/usr/bin/env bash
set -euo pipefail

create_database() {
  local database="$1"

  psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-SQL
    SELECT 'CREATE DATABASE ${database}'
    WHERE NOT EXISTS (
      SELECT FROM pg_database WHERE datname = '${database}'
    )\gexec
SQL
}

create_database auth_db
create_database short_db
create_database stats_db
