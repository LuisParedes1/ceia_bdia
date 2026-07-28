#!/bin/sh
# Objetivo: iniciar la UI oficial para inspeccionar el estado posterior al procesamiento Silver.
# Requiere / entradas: 02_procesar_silver.sql completo y puerto local publicado por Compose.
# Produce / modifica: mantiene una conexión DuckDB y estado operativo en el volumen existente.
# Resultado esperado: UI disponible en 127.0.0.1:DUCKDB_UI_PORT con las tablas de calidad.
# Seguridad: no ejecutar pasos SQL en otro proceso hasta detener la UI.
set -eu

. /scripts/_duckdb_ui.sh
puerto_host="${DUCKDB_UI_PORT:-4213}"

if duckdb_ui_activa; then
  echo "DuckDB UI ya está activa en http://127.0.0.1:$puerto_host."
  exit 0
fi

[ -f "$DUCKDB_UI_BASE" ] || {
  echo "No existe $DUCKDB_UI_BASE. Ejecutá primero los pasos 01 y 02." >&2
  exit 1
}

faltantes="$(duckdb -readonly "$DUCKDB_UI_BASE" -noheader -list -c "
WITH esperadas(nombre) AS (VALUES
  ('raw_usuarios'), ('raw_tipos_fuente'), ('raw_datasets'), ('raw_tipos_modelo'),
  ('raw_modelos'), ('raw_experimentos'), ('raw_experimentos_modelos'), ('raw_metricas'),
  ('evaluados_usuarios'), ('evaluados_tipos_fuente'), ('evaluados_datasets'), ('evaluados_tipos_modelo'),
  ('evaluados_modelos'), ('evaluados_experimentos'), ('evaluados_experimentos_modelos'), ('evaluados_metricas'),
  ('silver_usuarios'), ('silver_tipos_fuente'), ('silver_datasets'), ('silver_tipos_modelo'),
  ('silver_modelos'), ('silver_experimentos'), ('silver_experimentos_modelos'), ('silver_metricas'),
  ('rechazos'), ('resumen_calidad')
)
SELECT coalesce(string_agg(nombre, ', ' ORDER BY nombre), '')
FROM esperadas
WHERE nombre NOT IN (SELECT table_name FROM information_schema.tables WHERE table_schema = 'main');")"
if [ -n "$faltantes" ]; then
  echo "La UI requiere completar 02_procesar_silver.sql. Faltan: $faltantes" >&2
  exit 1
fi

mkdir -p "$DUCKDB_UI_STATE_DIR"
nohup sh /scripts/servidor_duckdb_ui.sh > "$DUCKDB_UI_LOG_FILE" 2>&1 &

intento=0
while [ "$intento" -lt 30 ]; do
  if curl -fsS "http://127.0.0.1:$DUCKDB_UI_PROXY_PORT/" >/dev/null 2>&1; then
    echo "DuckDB UI iniciada en http://127.0.0.1:$puerto_host."
    echo "Inspeccioná los datos y detenela antes de continuar con el pipeline."
    exit 0
  fi
  # El daemon escribe su propio PID al iniciar; se tolera el breve intervalo previo para
  # no confundir una carrera de planificación del contenedor con un fallo real.
  if [ "$intento" -ge 3 ] && ! duckdb_ui_activa; then
    echo "DuckDB UI no pudo iniciar. Revisá $DUCKDB_UI_LOG_FILE dentro del contenedor." >&2
    exit 1
  fi
  intento=$((intento + 1))
  sleep 1
done

echo "DuckDB UI no respondió dentro de 30 segundos. Revisá $DUCKDB_UI_LOG_FILE." >&2
exit 1
