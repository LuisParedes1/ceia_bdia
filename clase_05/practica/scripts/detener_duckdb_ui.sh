#!/bin/sh
# Objetivo: cerrar la conexión propietaria de DuckDB UI antes de transformar o publicar datos.
# Resultado esperado: comando idempotente; elimina estado PID obsoleto y libera la base.
set -eu

. /scripts/_duckdb_ui.sh

if ! duckdb_ui_activa; then
  echo "DuckDB UI ya está detenida."
  exit 0
fi

pid="$(duckdb_ui_pid)"
kill "$pid"
intento=0
while kill -0 "$pid" 2>/dev/null && [ "$intento" -lt 15 ]; do
  intento=$((intento + 1))
  sleep 1
done

if kill -0 "$pid" 2>/dev/null; then
  kill -KILL "$pid" 2>/dev/null || true
  sleep 1
fi
rm -f "$DUCKDB_UI_PID_FILE"
echo "DuckDB UI detenida; la base quedó disponible para continuar."
