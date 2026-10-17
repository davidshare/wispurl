#!/usr/bin/env bash
# Creates one least-privilege login per service, so no application connects as
# the postgres superuser.
#
#   auth_svc       owns auth_db   (runs its migrations, reads and writes its data)
#   shortener_svc  owns short_db
#   analytics_svc  owns stats_db  (used by the analytics API and its consumer)
#   cleanup_svc    may only read four columns of short_db.links and set is_active
#
# Each database refuses connections from everyone except its owner (and the
# grants below), so a compromised service can't reach another service's data.
#
# Postgres runs this automatically only when its data volume is first created
# (after create-databases.sh). For an existing volume, run it once by hand:
#   docker compose exec postgres bash /docker-entrypoint-initdb.d/create-service-roles.sh
# It is safe to re-run: it also resets the passwords to the current values.
set -euo pipefail

: "${POSTGRES_AUTH_PASSWORD:?POSTGRES_AUTH_PASSWORD must be set (see .env.example)}"
: "${POSTGRES_SHORTENER_PASSWORD:?POSTGRES_SHORTENER_PASSWORD must be set (see .env.example)}"
: "${POSTGRES_ANALYTICS_PASSWORD:?POSTGRES_ANALYTICS_PASSWORD must be set (see .env.example)}"
: "${POSTGRES_CLEANUP_PASSWORD:?POSTGRES_CLEANUP_PASSWORD must be set (see .env.example)}"

run_sql() {
  local database="$1"
  shift
  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$database" "$@"
}

# 1. Logins. No superuser, no CREATEDB, no CREATEROLE; a connection cap keeps a
#    runaway pool from exhausting max_connections.
run_sql "$POSTGRES_DB" \
  --set auth_password="$POSTGRES_AUTH_PASSWORD" \
  --set shortener_password="$POSTGRES_SHORTENER_PASSWORD" \
  --set analytics_password="$POSTGRES_ANALYTICS_PASSWORD" \
  --set cleanup_password="$POSTGRES_CLEANUP_PASSWORD" <<-'SQL'
  SELECT format('CREATE ROLE %I LOGIN', r)
  FROM unnest(ARRAY['auth_svc', 'shortener_svc', 'analytics_svc', 'cleanup_svc']) AS r
  WHERE NOT EXISTS (SELECT FROM pg_roles WHERE rolname = r)\gexec

  ALTER ROLE auth_svc      WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE CONNECTION LIMIT 20 PASSWORD :'auth_password';
  ALTER ROLE shortener_svc WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE CONNECTION LIMIT 20 PASSWORD :'shortener_password';
  ALTER ROLE analytics_svc WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE CONNECTION LIMIT 30 PASSWORD :'analytics_password';
  ALTER ROLE cleanup_svc   WITH LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE CONNECTION LIMIT 5  PASSWORD :'cleanup_password';

  -- Each service owns its database. In PostgreSQL 15+ the public schema is owned
  -- by pg_database_owner, so the new owner also gets the schema.
  ALTER DATABASE auth_db  OWNER TO auth_svc;
  ALTER DATABASE short_db OWNER TO shortener_svc;
  ALTER DATABASE stats_db OWNER TO analytics_svc;

  -- Nobody else may connect (PUBLIC can by default).
  REVOKE ALL ON DATABASE auth_db, short_db, stats_db FROM PUBLIC;
  GRANT CONNECT ON DATABASE short_db TO cleanup_svc;
SQL

# 2. Hand over tables created before this script ran (for example by migrations
#    that ran as postgres), so each service owns everything in its database.
transfer_ownership() {
  local database="$1" owner="$2"
  run_sql "$database" --set owner="$owner" <<-'SQL'
  SELECT format('ALTER TABLE public.%I OWNER TO %I', tablename, :'owner')
  FROM pg_tables
  WHERE schemaname = 'public' AND tableowner <> :'owner'\gexec
SQL
}

transfer_ownership auth_db auth_svc
transfer_ownership short_db shortener_svc
transfer_ownership stats_db analytics_svc

# 3. The cleanup worker's column grants on short_db.links are applied by the
#    shortener's migration 20261017_0003, because on a brand-new database the
#    table doesn't exist yet when this script runs. If links already exists
#    (an existing database), apply the same grant now.
run_sql short_db <<-'SQL'
  DO $$
  BEGIN
    IF to_regclass('public.links') IS NOT NULL THEN
      GRANT USAGE ON SCHEMA public TO cleanup_svc;
      GRANT SELECT (id, short_code, is_active, expires_at), UPDATE (is_active)
        ON public.links TO cleanup_svc;
    END IF;
  END
  $$;
SQL
