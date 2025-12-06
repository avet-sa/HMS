#!/bin/bash
set -euo pipefail

# This script runs during container initialization (when the DB volume is empty).
# It ensures a `postgres` role exists and has the correct password, and grants
# privileges on the configured database.

# `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` are provided by the
# official postgres image entrypoint environment.

psql_cmd() {
  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -c "$1"
}

# Wait a short moment (shouldn't be necessary during init, but safe)
sleep 1

# Check if role 'postgres' exists
if psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -c "SELECT 1 FROM pg_roles WHERE rolname='postgres'" | grep -q 1; then
  echo "Role 'postgres' already exists."
else
  echo "Creating role 'postgres'..."
  # Create postgres role with superuser and provided password
  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<EOF
    CREATE ROLE postgres WITH LOGIN SUPERUSER PASSWORD '$POSTGRES_PASSWORD';
    GRANT ALL PRIVILEGES ON DATABASE "$POSTGRES_DB" TO postgres;
EOF
  echo "Role 'postgres' created."
fi

# Ensure schema privileges (best-effort)
psql_cmd "CREATE SCHEMA IF NOT EXISTS public;"
psql_cmd "GRANT ALL PRIVILEGES ON SCHEMA public TO postgres;"

echo "init-db.sh completed."
