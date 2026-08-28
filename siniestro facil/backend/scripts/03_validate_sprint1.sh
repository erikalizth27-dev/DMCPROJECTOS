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

echo "Validando migración Alembic"
current_revision="$(alembic current 2>/dev/null | tail -n 1)"
if [[ "$current_revision" != "20260828_02 (head)" ]]; then
  echo "ERROR: revisión inesperada: $current_revision" >&2
  exit 1
fi
echo "OK: $current_revision"

python - <<'PY'
import os

from sqlalchemy import create_engine, text

engine = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)

with engine.connect() as connection:
    database, user = connection.execute(
        text("SELECT current_database(), current_user")
    ).one()
    revision = connection.execute(
        text("SELECT version_num FROM siniestro_facil.alembic_version")
    ).scalar_one()
    tables = connection.execute(
        text("""
            SELECT count(*)
            FROM information_schema.tables
            WHERE table_schema = 'siniestro_facil'
        """)
    ).scalar_one()
    required = connection.execute(
        text("""
            SELECT
                to_regclass('siniestro_facil.solicitud_idempotente'),
                to_regclass('siniestro_facil.identidad_actor')
        """)
    ).one()
    can_create = connection.execute(
        text("""
            SELECT has_schema_privilege(
                current_user, 'siniestro_facil', 'CREATE'
            )
        """)
    ).scalar_one()
    can_reference = connection.execute(
        text("""
            SELECT
                has_table_privilege(
                    current_user,
                    'siniestro_facil.asegurado',
                    'REFERENCES'
                )
                OR has_table_privilege(
                    current_user,
                    'siniestro_facil.usuario_interno',
                    'REFERENCES'
                )
                OR has_table_privilege(
                    current_user,
                    'siniestro_facil.proveedor',
                    'REFERENCES'
                )
        """)
    ).scalar_one()
    identity_residue = connection.execute(
        text("""
            SELECT count(*)
            FROM siniestro_facil.identidad_actor
            WHERE tenant_id = 'tenant-s1-be-03'
        """)
    ).scalar_one()
    idempotency_residue = connection.execute(
        text("""
            SELECT count(*)
            FROM siniestro_facil.solicitud_idempotente
            WHERE clave LIKE 's1-be-02-cloudsql-%'
        """)
    ).scalar_one()

assert database == "DMCSINIESTROFACIL", database
assert user == "siniestro_app", user
assert revision == "20260828_02", revision
assert tables >= 26, tables
assert all(required), required
assert can_create is False, can_create
assert can_reference is False, can_reference
assert identity_residue == 0, identity_residue
assert idempotency_residue == 0, idempotency_residue

print(f"OK: base={database} usuario={user} tablas={tables}")
print("OK: tablas Sprint 1 presentes")
print("OK: privilegios temporales retirados")
print("OK: sin residuos de pruebas integradas")
PY

echo "Validando compilación"
python -m compileall -q src tests alembic
echo "OK: compilación"

echo "Ejecutando suite completa"
python -m pytest -v

echo "SPRINT 1 VALIDACIÓN INTEGRAL: OK"
