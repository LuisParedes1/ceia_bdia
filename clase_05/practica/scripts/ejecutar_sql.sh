#!/bin/sh
# Objetivo: ejecutar un SQL de la práctica con el entorno común de DuckDB preparado.
# Requiere / entradas: ruta /sql/NN_archivo.sql y variables de conexión de los servicios.
# Produce / modifica: clase_05.duckdb y, para la carga Gold, el Warehouse PostgreSQL.
# Resultado esperado: script ejecutado con acceso a MinIO y estado DuckDB persistente.
# Guía: andamiaje compartido por pasos manuales y por la automatización del pipeline.
# Seguridad: rechaza toda ejecución mientras la UI posee la conexión a la base.
set -eu

archivo="${1:?Uso: ejecutar_sql.sh /sql/NN_archivo.sql}"
base="/workspace/clase_05.duckdb"

# Separar inspección y transformación hace visible la exclusión entre procesos de DuckDB:
# el estudiante debe cerrar la UI antes de continuar con cualquier paso manual.
. /scripts/_duckdb_ui.sh
if duckdb_ui_activa; then
  echo "No se puede ejecutar $archivo mientras DuckDB UI está activa." >&2
  echo "Detenela con: docker compose exec -T duckdb-transformer sh /scripts/detener_duckdb_ui.sh" >&2
  exit 1
fi

# La base persistente comparte las tablas entre pasos. httpfs y el secret S3 habilitan MinIO
# sin repetir credenciales ni configuración de transporte en cada archivo didáctico.
configuracion="INSTALL httpfs; LOAD httpfs;
CREATE OR REPLACE SECRET minio_local (
  TYPE s3,
  KEY_ID '$MINIO_ROOT_USER',
  SECRET '$MINIO_ROOT_PASSWORD',
  REGION 'us-east-1',
  ENDPOINT 'minio-storage:9000',
  URL_STYLE 'path',
  USE_SSL false
);"

case "$archivo" in
  */04_*)
    # Sólo el rol 04 carga Gold: adjuntar PostgreSQL antes ampliaría privilegios y
    # dependencias de scripts que únicamente necesitan DuckDB y MinIO.
    configuracion="$configuracion
INSTALL postgres; LOAD postgres;
ATTACH 'host=postgres-warehouse port=5432 dbname=$POSTGRES_DB user=$POSTGRES_USER password=$POSTGRES_PASSWORD' AS pg (TYPE postgres);"
    ;;
esac

duckdb "$base" -c "$configuracion" -c ".read $archivo"
