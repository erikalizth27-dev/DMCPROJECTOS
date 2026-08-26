#!/usr/bin/env bash
set -Eeuo pipefail

TEMP_DIR="$(mktemp -d)"
SERVER_PID=""

cleanup() {
    if [[ -n "$SERVER_PID" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
    rm -rf -- "$TEMP_DIR"
}
trap cleanup EXIT INT TERM

free_port() {
    python -c "import socket; s=socket.socket(); s.bind(('127.0.0.1', 0)); print(s.getsockname()[1]); s.close()"
}

wait_for_server() {
    local port="$1"
    for _ in {1..30}; do
        if curl --silent --output /dev/null "http://127.0.0.1:${port}/health/live"; then
            return 0
        fi
        if ! kill -0 "$SERVER_PID" 2>/dev/null; then
            echo "ERROR: Uvicorn terminó inesperadamente." >&2
            return 1
        fi
        sleep 0.2
    done
    echo "ERROR: Uvicorn no quedó disponible en el puerto $port." >&2
    return 1
}

stop_server() {
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
    SERVER_PID=""
}

assert_case() {
    local case_name="$1"
    local expected_error="$2"
    shift 2
    local port response_file status
    port="$(free_port)"
    response_file="$TEMP_DIR/${case_name}.json"

    env "$@" uvicorn siniestro_facil.main:app \
        --host=127.0.0.1 --port="$port" \
        >"$TEMP_DIR/${case_name}.log" 2>&1 &
    SERVER_PID="$!"
    wait_for_server "$port"

    status="$(
        curl --silent --show-error \
            --output "$response_file" \
            --write-out '%{http_code}' \
            "http://127.0.0.1:${port}/health/ready"
    )"

    python - "$response_file" "$status" "$expected_error" <<'PY'
import json
import sys

path, status, expected_error = sys.argv[1:]
payload = json.loads(open(path, encoding="utf-8").read())
assert status == "503", f"HTTP esperado 503, recibido {status}"
assert payload["status"] == "not_ready", payload
assert expected_error in payload["errors"], payload
PY

    stop_server
    echo "OK: $case_name devolvió HTTP 503 y el error esperado."
}

assert_case \
    "database_url_ausente" \
    "DATABASE_URL no configurada" \
    -u DATABASE_URL \
    DATABASE_SCHEMA=siniestro_facil

assert_case \
    "esquema_invalido" \
    "DATABASE_SCHEMA debe ser siniestro_facil" \
    DATABASE_URL=postgresql+psycopg://invalid@127.0.0.1:1/invalid \
    DATABASE_SCHEMA=otro_esquema

echo "OK: las 2 validaciones negativas de readiness finalizaron correctamente."
