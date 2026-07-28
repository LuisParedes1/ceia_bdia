#!/bin/sh
# Objetivo: mantener el proceso oficial DuckDB UI y su proxy loopback bajo un único PID.
# Uso interno: iniciar_duckdb_ui.sh administra este proceso; no se invoca manualmente.
set -eu

. /scripts/_duckdb_ui.sh
fifo="$DUCKDB_UI_STATE_DIR/entrada.sql"
duckdb_pid=""
proxy_pid=""

limpiar() {
  trap - EXIT INT TERM
  [ -z "$proxy_pid" ] || kill "$proxy_pid" 2>/dev/null || true
  [ -z "$duckdb_pid" ] || kill "$duckdb_pid" 2>/dev/null || true
  exec 3>&- 2>/dev/null || true
  rm -f "$fifo"
  if [ "$(duckdb_ui_pid 2>/dev/null || true)" = "$$" ]; then
    rm -f "$DUCKDB_UI_PID_FILE"
  fi
}

trap 'exit 0' INT TERM
trap limpiar EXIT
mkdir -p "$DUCKDB_UI_STATE_DIR"
rm -f "$fifo"
mkfifo "$fifo"
printf '%s\n' "$$" > "$DUCKDB_UI_PID_FILE"

# El descriptor de escritura queda abierto para que la CLI no reciba EOF. Al terminar esta
# envoltura se cierra la conexión propietaria y, con ella, el servidor embebido oficial.
exec 3<> "$fifo"
duckdb "$DUCKDB_UI_BASE" < "$fifo" &
duckdb_pid=$!
printf '%s\n' \
  "LOAD ui;" \
  "SET ui_local_port = $DUCKDB_UI_INTERNAL_PORT;" \
  "CALL start_ui_server();" >&3

# DuckDB escucha sólo en loopback. El proxy expone un puerto interno de Compose que el host
# publica exclusivamente sobre 127.0.0.1, sin recurrir a network_mode: host.
socat "TCP-LISTEN:$DUCKDB_UI_PROXY_PORT,reuseaddr,fork,bind=0.0.0.0" \
  "TCP6:[::1]:$DUCKDB_UI_INTERNAL_PORT" &
proxy_pid=$!
wait "$duckdb_pid"
