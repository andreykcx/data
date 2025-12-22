#!/usr/bin/env sh
set -eu

echo "Running database migrations before starting the API..."
python - <<'PY'
import sys
from backend.app.db import run_migrations_with_retry

success = run_migrations_with_retry()
if not success:
    sys.exit("Database migrations failed; exiting.")
PY

exec "$@"
