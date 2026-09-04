#!/usr/bin/env bash
set -euo pipefail

BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_DIR="$(cd "${BACKEND_DIR}/../.." && pwd)"
cd "${BACKEND_DIR}"

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "ERROR: DATABASE_URL no configurada"
  exit 1
fi

echo "1/7 — Compilación"
python -m compileall -q src tests alembic
echo "Compilación: OK"

echo "2/7 — Suite completa"
python -m pytest -q
echo "Suite completa: OK"

echo "3/7 — Alembic"
ALEMBIC_CURRENT="$(alembic current)"
echo "${ALEMBIC_CURRENT}"
grep -q "20260903_04 (head)" <<<"${ALEMBIC_CURRENT}"
echo "Alembic 20260903_04 (head): OK"

echo "4/7 — Archivos sensibles"
cd "${REPO_DIR}"
if git ls-files | grep -Eq '(^|/).env$|.(pem|key|p12|pfx)$'; then
  echo "ERROR: archivo sensible rastreado por Git"
  git ls-files | grep -E '(^|/).env$|.(pem|key|p12|pfx)$'
  exit 1
fi
echo "Archivos sensibles no rastreados: OK"
cd "${BACKEND_DIR}"

echo "5/7 — S6-BE-01 PostgreSQL"
python scripts/24_validate_s6_be_01_postgresql.py

echo "6/7 — S6-BE-02 PostgreSQL"
python scripts/25_validate_s6_be_02_postgresql.py

echo "7/7 — S6-BE-03 PostgreSQL"
python scripts/26_validate_s6_be_03_postgresql.py

echo "SPRINT 6 — VALIDACIÓN INTEGRAL COMPLETADA"
