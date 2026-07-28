#!/bin/sh
# Estado compartido por los comandos de DuckDB UI. Este archivo se importa; no se ejecuta.

DUCKDB_UI_STATE_DIR="/workspace/.duckdb-ui"
DUCKDB_UI_PID_FILE="$DUCKDB_UI_STATE_DIR/servidor.pid"
DUCKDB_UI_LOG_FILE="$DUCKDB_UI_STATE_DIR/servidor.log"
DUCKDB_UI_BASE="/workspace/clase_05.duckdb"
DUCKDB_UI_INTERNAL_PORT=4213
DUCKDB_UI_PROXY_PORT=4214

duckdb_ui_pid() {
  [ -f "$DUCKDB_UI_PID_FILE" ] || return 1
  IFS= read -r pid < "$DUCKDB_UI_PID_FILE" || return 1
  case "$pid" in
    ''|*[!0-9]*) return 1 ;;
  esac
  printf '%s\n' "$pid"
}

duckdb_ui_activa() {
  pid="$(duckdb_ui_pid 2>/dev/null || true)"
  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
    comando="$(tr '\000' ' ' < "/proc/$pid/cmdline" 2>/dev/null || true)"
    case "$comando" in
      *servidor_duckdb_ui.sh*) return 0 ;;
    esac
  fi

  # Un PID inválido o reutilizado no debe bloquear futuras ejecuciones.
  rm -f "$DUCKDB_UI_PID_FILE"
  return 1
}
