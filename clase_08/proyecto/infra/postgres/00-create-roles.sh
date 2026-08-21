#!/bin/sh
set -eu

psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" --set=db_password="$POSTGRES_PASSWORD" <<'SQL'
CREATE EXTENSION IF NOT EXISTS vector;
CREATE ROLE project_owner NOLOGIN NOSUPERUSER NOBYPASSRLS;
ALTER SCHEMA public OWNER TO project_owner;
SELECT format('CREATE ROLE project_migrator LOGIN NOSUPERUSER NOBYPASSRLS PASSWORD %L', :'db_password');
\gexec
SELECT format('CREATE ROLE app_runtime LOGIN NOSUPERUSER NOBYPASSRLS PASSWORD %L', :'db_password');
\gexec
SELECT format('CREATE ROLE assistant_reader LOGIN NOSUPERUSER NOBYPASSRLS PASSWORD %L', :'db_password');
\gexec
GRANT project_owner TO project_migrator;
SQL
