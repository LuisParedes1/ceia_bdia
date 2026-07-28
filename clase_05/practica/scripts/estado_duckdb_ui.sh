#!/bin/sh
# Objetivo: informar si el proceso y el endpoint interno de DuckDB UI están disponibles.
set -eu

. /scripts/_duckdb_ui.sh
puerto_host="${DUCKDB_UI_PORT:-4213}"

if ! duckdb_ui_activa; then
  echo "DuckDB UI está detenida."
  exit 1
fi

if curl -fsS "http://127.0.0.1:$DUCKDB_UI_PROXY_PORT/" >/dev/null 2>&1; then
  echo "DuckDB UI está activa en http://127.0.0.1:$puerto_host (PID $(duckdb_ui_pid))."
  exit 0
fi

echo "DuckDB UI tiene un proceso activo, pero el endpoint todavía no responde." >&2
exit 1
