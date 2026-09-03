#!/usr/bin/env bash
set -euo pipefail

EXPECTED_REVISION="20260902_05"

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "ERROR: DATABASE_URL no está configurada. Carga .env antes de ejecutar."
  exit 1
fi

echo "1/6 — Compilación"
python -m compileall -q src tests alembic scripts

echo "2/6 — Suite completa"
python -m pytest -v

echo "3/6 — Revisión Alembic"
CURRENT_REVISION="$(alembic current 2>/dev/null | awk 'NF {print $1}' | tail -n 1)"
if [[ "$CURRENT_REVISION" != "$EXPECTED_REVISION" ]]; then
  echo "ERROR: Alembic está en $CURRENT_REVISION; se esperaba $EXPECTED_REVISION"
  exit 1
fi
echo "$CURRENT_REVISION (head): OK"

echo "4/6 — S4-BE-01 PostgreSQL"
python scripts/09_validate_s4_be_01_postgresql.py

echo "5/6 — S4-BE-02 PostgreSQL"
python scripts/11_validate_s4_be_02_postgresql.py

echo "6/6 — S4-BE-03 PostgreSQL"
python scripts/13_validate_s4_be_03_postgresql.py

echo "SPRINT 4 — VALIDACIÓN INTEGRAL COMPLETADA"
