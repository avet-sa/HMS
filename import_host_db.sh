#!/bin/bash
set -euo pipefail

# import_host_db.sh
# Streams a dump from host Postgres into the Compose DB when ENABLE_IMPORT_HOST_DB=true

ENABLE_IMPORT_HOST_DB=${ENABLE_IMPORT_HOST_DB:-false}
if [ "${ENABLE_IMPORT_HOST_DB}" = "true" ]; then
  echo "Importing host DB '${HOST_DB_NAME:-hms}' into container DB '${DB_NAME:-hms}'..."
  # Use host.docker.internal to reach host from Docker on Windows
  # Use --clean --if-exists to drop/recreate objects safely (if-exists prevents errors on missing objects)
  PGPASSWORD="${HOST_DB_PASSWORD}" pg_dump -h "${HOST_DB_HOST:-host.docker.internal}" -U "${HOST_DB_USER:-postgres}" -Fc "${HOST_DB_NAME:-hms}" \
    | PGPASSWORD="${DB_PASSWORD}" pg_restore -h "${DB_HOST:-db}" -U "${DB_USER}" -d "${DB_NAME}" --clean --if-exists --exit-on-error
  echo "Import finished."
else
  echo "Host import disabled (set ENABLE_IMPORT_HOST_DB=true to enable)."
fi
