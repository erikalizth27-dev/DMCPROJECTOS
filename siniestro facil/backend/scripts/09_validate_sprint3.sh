#!/usr/bin/env bash
set -euo pipefail

backend_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$backend_dir"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "ERROR: DATABASE_URL no configurada" >&2
  exit 1
fi

export GCP_PROJECT_ID="${GCP_PROJECT_ID:-project-77c17016-86bc-4fc4-a97}"

echo "1/8 — Compilación"
python -m compileall -q src tests alembic

echo "2/8 — Regresión completa"
python -m pytest -v

echo "3/8 — Revisión Alembic"
current_revision="$(alembic current 2>/dev/null | tail -n 1)"
if [[ "$current_revision" != "20260902_02 (head)" ]]; then
  echo "ERROR: revisión inesperada: $current_revision" >&2
  exit 1
fi
echo "Alembic: $current_revision"

echo "4/8 — S3-BE-01 PostgreSQL"
python scripts/05_validate_s3_be_01_postgresql.py

echo "5/8 — S3-BE-02 PostgreSQL"
python scripts/06_validate_s3_be_02_postgresql.py

echo "6/8 — S3-BE-03 outbox PostgreSQL"
python scripts/07_validate_s3_be_03_outbox_postgresql.py

echo "7/8 — Recursos GCP"
gcloud pubsub subscriptions describe   siniestro-asistencia-worker   --project="$GCP_PROJECT_ID"   --format="value(state)"   | grep -qx "ACTIVE"

gcloud pubsub subscriptions describe   siniestro-asistencia-dead-letter-monitor   --project="$GCP_PROJECT_ID"   --format="value(state)"   | grep -qx "ACTIVE"

gcloud tasks queues describe   siniestro-asistencia-reintentos   --location=us-central1   --project="$GCP_PROJECT_ID"   --format="value(state)"   | grep -qx "RUNNING"

echo "Recursos GCP: OK"

echo "8/8 — Pub/Sub y Cloud Tasks reales"
python scripts/08_validate_s3_be_03_gcp.py

echo "SPRINT 3 — VALIDACIÓN INTEGRAL COMPLETADA"
