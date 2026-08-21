#!/usr/bin/env bash
set -Eeuo pipefail

GCP_PROJECT_ID="${GCP_PROJECT_ID:-project-77c17016-86bc-4fc4-a97}"
CLOUDSQL_INSTANCE="${CLOUDSQL_INSTANCE:-dmcappasistidaia}"
CLOUDSQL_DATABASE="${CLOUDSQL_DATABASE:-DMCSINIESTROFACIL}"
EXPECTED_TABLES="${EXPECTED_TABLES:-22}"
CLOUDSQL_LOCAL_PORT="${CLOUDSQL_LOCAL_PORT:-}"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DDL_FILE="$SCRIPT_DIR/01_schema.sql"
TEST_FILE="$SCRIPT_DIR/02_test_constraints.sql"
CONTROL_SQL=""

cleanup() {
    unset PGPASSWORD || true
    if [[ -n "$CONTROL_SQL" && -f "$CONTROL_SQL" ]]; then
        rm -f -- "$CONTROL_SQL"
    fi
}
trap cleanup EXIT

fail() {
    echo "ERROR: $*" >&2
    exit 1
}

for command_name in gcloud git python3; do
    command -v "$command_name" >/dev/null 2>&1 || fail "No se encontró $command_name."
done

[[ -f "$DDL_FILE" ]] || fail "No existe el DDL: $DDL_FILE"
[[ -f "$TEST_FILE" ]] || fail "No existen las pruebas: $TEST_FILE"

if [[ -z "$CLOUDSQL_LOCAL_PORT" ]]; then
    CLOUDSQL_LOCAL_PORT="$(python3 - <<'PY'
import socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind(('127.0.0.1', 0))
    print(sock.getsockname()[1])
PY
)"
fi

[[ "$CLOUDSQL_LOCAL_PORT" =~ ^[0-9]+$ ]] || fail "Puerto local inválido: $CLOUDSQL_LOCAL_PORT"

ACTIVE_ACCOUNT="$(gcloud auth list --filter='status:ACTIVE' --format='value(account)' | head -n 1)"
[[ -n "$ACTIVE_ACCOUNT" ]] || fail "No existe una cuenta activa en gcloud."

PROJECT_NAME="$(
    gcloud projects describe "$GCP_PROJECT_ID" \
        --format='value(name)' 2>/dev/null
)"
[[ "$PROJECT_NAME" == "My First Project" ]] || \
    fail "El proyecto $GCP_PROJECT_ID no corresponde a 'My First Project' (obtenido: $PROJECT_NAME)."

readarray -t INSTANCE_DATA < <(
    gcloud sql instances describe "$CLOUDSQL_INSTANCE" \
        --project="$GCP_PROJECT_ID" \
        --format='value(state,databaseVersion,region,connectionName)' 2>/dev/null
)
[[ ${#INSTANCE_DATA[@]} -gt 0 ]] || fail "No se encontró la instancia $CLOUDSQL_INSTANCE."

read -r INSTANCE_STATE DATABASE_VERSION INSTANCE_REGION CONNECTION_NAME <<<"${INSTANCE_DATA[0]}"
[[ "$INSTANCE_STATE" == "RUNNABLE" ]] || fail "La instancia no está RUNNABLE: $INSTANCE_STATE"
[[ "$DATABASE_VERSION" == POSTGRES_* ]] || fail "La instancia no es PostgreSQL: $DATABASE_VERSION"

DATABASE_FOUND="$(
    gcloud sql databases list \
        --project="$GCP_PROJECT_ID" \
        --instance="$CLOUDSQL_INSTANCE" \
        --filter="name=$CLOUDSQL_DATABASE" \
        --format='value(name)'
)"
[[ "$DATABASE_FOUND" == "$CLOUDSQL_DATABASE" ]] || \
    fail "No se encontró la base $CLOUDSQL_DATABASE respetando mayúsculas."

echo "Destino validado:"
echo "  Cuenta:         $ACTIVE_ACCOUNT"
echo "  Proyecto:       $PROJECT_NAME ($GCP_PROJECT_ID)"
echo "  Instancia:      $CLOUDSQL_INSTANCE"
echo "  Motor:          $DATABASE_VERSION"
echo "  Región:         $INSTANCE_REGION"
echo "  Connection:     $CONNECTION_NAME"
echo "  Base de datos:  $CLOUDSQL_DATABASE"
echo "  Puerto local:   $CLOUDSQL_LOCAL_PORT"
echo "  DDL:            $DDL_FILE"
echo "  Pruebas:        $TEST_FILE"
echo

read -r -p "Escriba DESPLEGAR para continuar: " CONFIRMATION
[[ "$CONFIRMATION" == "DESPLEGAR" ]] || fail "Operación cancelada."

read -r -s -p "Contraseña del usuario postgres: " PGPASSWORD
echo
[[ -n "$PGPASSWORD" ]] || fail "La contraseña no puede estar vacía."
export PGPASSWORD

CONTROL_SQL="$(mktemp /tmp/dmcsiniestrofacil-deploy.XXXXXX.sql)"
chmod 600 "$CONTROL_SQL"

cat >"$CONTROL_SQL" <<SQL
\set ON_ERROR_STOP on
\echo 'Validando conexión y estado inicial...'
SELECT CASE
    WHEN current_database() = '$CLOUDSQL_DATABASE' THEN 1
    ELSE 1 / 0
END AS conexion_validada;

SELECT CASE
    WHEN NOT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'siniestro_facil'
          AND table_type = 'BASE TABLE'
    ) THEN 1
    ELSE 1 / 0
END AS esquema_vacio_validado;

\echo 'Desplegando modelo físico...'
\i '$DDL_FILE'

\echo 'Ejecutando pruebas de constraints...'
\i '$TEST_FILE'

SELECT count(*) AS tablas_desplegadas
FROM information_schema.tables
WHERE table_schema = 'siniestro_facil'
  AND table_type = 'BASE TABLE';

SELECT CASE
    WHEN count(*) = $EXPECTED_TABLES THEN 1
    ELSE 1 / 0
END AS cantidad_tablas_validada
FROM information_schema.tables
WHERE table_schema = 'siniestro_facil'
  AND table_type = 'BASE TABLE';

\echo 'OK: modelo desplegado y validado con $EXPECTED_TABLES tablas.'
SQL

echo "Conectando y ejecutando despliegue..."
gcloud sql connect "$CLOUDSQL_INSTANCE" \
    --project="$GCP_PROJECT_ID" \
    --user=postgres \
    --database="$CLOUDSQL_DATABASE" \
    --port="$CLOUDSQL_LOCAL_PORT" \
    --quiet <"$CONTROL_SQL"

echo "Despliegue finalizado correctamente."
