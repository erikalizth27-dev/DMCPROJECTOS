#!/usr/bin/env bash
set -euo pipefail

BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$BACKEND_DIR"

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "ERROR: DATABASE_URL no configurada" >&2
  exit 1
fi

echo "1/6 — Compilación"
python -m compileall -q src tests alembic
echo "Compilación: OK"

echo "2/6 — Regresión"
python -m pytest -q

echo "3/6 — Alembic"
CURRENT_REVISION="$(alembic current)"
echo "$CURRENT_REVISION"
if [[ "$CURRENT_REVISION" != *"20260903_03 (head)"* ]]; then
  echo "ERROR: revisión Alembic inesperada" >&2
  exit 1
fi

echo "4/6 — S5-BE-01 PostgreSQL"
python scripts/17_validate_s5_be_01_postgresql.py

echo "5/6 — S5-BE-02 PostgreSQL"
python scripts/19_validate_s5_be_02_postgresql.py

echo "6/6 — S5-BE-03 PostgreSQL"
python scripts/21_validate_s5_be_03_postgresql.py

echo "SPRINT 5 — VALIDACIÓN INTEGRAL COMPLETADA"
