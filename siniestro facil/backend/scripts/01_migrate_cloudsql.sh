#!/usr/bin/env bash
set -Eeuo pipefail

GCP_PROJECT_ID="${GCP_PROJECT_ID:-project-77c17016-86bc-4fc4-a97}"
CLOUDSQL_INSTANCE="${CLOUDSQL_INSTANCE:-dmcappasistidaia}"
CLOUDSQL_DATABASE="${CLOUDSQL_DATABASE:-DMCSINIESTROFACIL}"
CLOUDSQL_USER="${CLOUDSQL_USER:-postgres}"
EXPECTED_REVISION="20260825_01"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
PROXY_PID=""

cleanup() {
    unset PGPASSWORD DATABASE_URL
    if [[ -n "$PROXY_PID" ]] && kill -0 "$PROXY_PID" 2>/dev/null; then
        kill "$PROXY_PID" 2>/dev/null || true
        wait "$PROXY_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

for command_name in gcloud cloud-sql-proxy python alembic; do
    command -v "$command_name" >/dev/null 2>&1 || {
        echo "ERROR: falta el comando $command_name." >&2
        exit 1
    }
done

ACTIVE_PROJECT="$(gcloud config get-value project 2>/dev/null)"
if [[ "$ACTIVE_PROJECT" != "$GCP_PROJECT_ID" ]]; then
    echo "ERROR: proyecto activo [$ACTIVE_PROJECT], esperado [$GCP_PROJECT_ID]." >&2
    exit 1
fi

INSTANCE_CONNECTION_NAME="$(
    gcloud sql instances describe "$CLOUDSQL_INSTANCE" \
        --project="$GCP_PROJECT_ID" \
        --format='value(connectionName)'
)"

INSTANCE_STATE="$(
    gcloud sql instances describe "$CLOUDSQL_INSTANCE" \
        --project="$GCP_PROJECT_ID" \
        --format='value(state)'
)"

[[ "$INSTANCE_STATE" == "RUNNABLE" ]] || {
    echo "ERROR: instancia en estado [$INSTANCE_STATE], se esperaba RUNNABLE." >&2
    exit 1
}

DATABASE_FOUND="$(
    gcloud sql databases list \
        --project="$GCP_PROJECT_ID" \
        --instance="$CLOUDSQL_INSTANCE" \
        --filter="name=$CLOUDSQL_DATABASE" \
        --format='value(name)'
)"

[[ "$DATABASE_FOUND" == "$CLOUDSQL_DATABASE" ]] || {
    echo "ERROR: no se encontró la base exacta [$CLOUDSQL_DATABASE]." >&2
    exit 1
}

LOCAL_PORT="$(
    python -c "import socket; s=socket.socket(); s.bind(('127.0.0.1', 0)); print(s.getsockname()[1]); s.close()"
)"

echo "Destino validado:"
printf '  Proyecto:  %s\n' "$GCP_PROJECT_ID"
printf '  Instancia: %s\n' "$CLOUDSQL_INSTANCE"
printf '  Base:      %s\n' "$CLOUDSQL_DATABASE"
printf '  Revisión:  %s\n' "$EXPECTED_REVISION"

read -r -p "Escriba MIGRAR para continuar: " CONFIRMATION
[[ "$CONFIRMATION" == "MIGRAR" ]] || {
    echo "Operación cancelada sin cambios."
    exit 0
}

read -r -s -p "Contraseña PostgreSQL de $CLOUDSQL_USER: " PGPASSWORD
echo
export PGPASSWORD

cloud-sql-proxy "$INSTANCE_CONNECTION_NAME" \
    --address=127.0.0.1 \
    --port="$LOCAL_PORT" \
    >/tmp/siniestro-facil-cloud-sql-proxy.log 2>&1 &
PROXY_PID="$!"

for _ in {1..30}; do
    if (echo >/dev/tcp/127.0.0.1/"$LOCAL_PORT") 2>/dev/null; then
        break
    fi
    if ! kill -0 "$PROXY_PID" 2>/dev/null; then
        echo "ERROR: Cloud SQL Proxy terminó inesperadamente." >&2
        sed -n '1,80p' /tmp/siniestro-facil-cloud-sql-proxy.log >&2
        exit 1
    fi
    sleep 1
done

(echo >/dev/tcp/127.0.0.1/"$LOCAL_PORT") 2>/dev/null || {
    echo "ERROR: el proxy no quedó disponible en el puerto $LOCAL_PORT." >&2
    exit 1
}

export DATABASE_URL="postgresql+psycopg://${CLOUDSQL_USER}@127.0.0.1:${LOCAL_PORT}/${CLOUDSQL_DATABASE}"

cd "$BACKEND_DIR"
alembic upgrade head

CURRENT_REVISION="$(alembic current | awk 'NF {print $1; exit}')"
[[ "$CURRENT_REVISION" == "$EXPECTED_REVISION" ]] || {
    echo "ERROR: revisión actual [$CURRENT_REVISION], esperada [$EXPECTED_REVISION]." >&2
    exit 1
}

echo "OK: migración aplicada y revisión $CURRENT_REVISION validada."
