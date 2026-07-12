# BDIA - Práctica Clase 4

Práctica de fundamentos NoSQL y modelado documental con MongoDB. MongoDB Compass es el cliente principal; Docker ejecuta MongoDB y ofrece Mongo Express como visor web opcional.

## Ruta rápida

Requisitos externos:

- Docker Desktop o Docker Engine con Docker Compose.
- MongoDB Compass instalado en el equipo.
- Git.

Desde `clase_04/practica`:

```bash
cp .env.example .env
docker compose up -d
docker compose ps
```

En Windows PowerShell, usá `Copy-Item .env.example .env`.

Cuando `mongodb` figure como saludable, cargá los datos:

```bash
docker compose exec -e MONGO_DATABASE=bdia_clase4 mongodb mongosh --quiet --username bdia_admin --password bdia_local_pass --authenticationDatabase admin /scripts/00_cargar_datos.js
```

Conectá Compass con esta URI predeterminada:

```text
mongodb://bdia_admin:bdia_local_pass@localhost:27017/?authSource=admin
```

Si modificaste `MONGO_LISTEN_PORT` o las credenciales, ajustá la URI. Compass se conecta a `localhost:${MONGO_LISTEN_PORT}`; el host `mongodb` solo existe dentro de la red de Docker.

Luego abrí [`consultas/01_revisar_origen_relacional.md`](consultas/01_revisar_origen_relacional.md) y recorré en orden los ejercicios `01` a `08`. Los `.md` se leen en el editor o navegador; copiá sus bloques JavaScript al shell integrado de Compass y ejecutalos como indica cada ejercicio.

## Flujo de trabajo

- Docker y `mongosh` ejecutan únicamente `00_cargar_datos.js` para preparar o reiniciar la base.
- Compass es el espacio de trabajo principal para filtros, agregaciones, CRUD, índices y `explain` de `consultas/01..08`.
- Compass no accede a `/scripts`: esa ruta existe únicamente dentro del contenedor `mongodb`.
- Mongo Express queda como visor opcional en <http://localhost:8081>; no reemplaza la consola ni las herramientas de consulta de Compass.

La guía operativa está en [`docs/guia-practica.md`](docs/guia-practica.md).

## Configuración

`.env.example` define credenciales didácticas y puertos locales:

| Variable | Valor predeterminado | Uso |
| --- | --- | --- |
| `MONGO_INITDB_ROOT_USERNAME` | `bdia_admin` | Usuario administrador local. |
| `MONGO_INITDB_ROOT_PASSWORD` | `bdia_local_pass` | Contraseña local. |
| `MONGO_DATABASE` | `bdia_clase4` | Base usada por los scripts. |
| `MONGO_LISTEN_PORT` | `27017` | Puerto de MongoDB para Compass. |
| `ME_CONFIG_BASICAUTH_USERNAME` | `admin` | Usuario web de Mongo Express. |
| `ME_CONFIG_BASICAUTH_PASSWORD` | `admin_local` | Contraseña web de Mongo Express. |
| `MONGO_EXPRESS_LISTEN_PORT` | `8081` | Puerto web de Mongo Express. |

Los puertos se publican únicamente en `127.0.0.1`. Estas credenciales son solo para la práctica local y no deben reutilizarse en producción.

## Servicios

| Servicio | Uso | Acceso predeterminado |
| --- | --- | --- |
| `mongodb` | Servidor MongoDB 8.0.12 y ejecución de scripts con `mongosh`. | `localhost:27017` |
| `mongo-express` | Visor web opcional de bases, colecciones y documentos. | <http://localhost:8081> |

Mongo Express solicita `admin` / `admin_local`. Si cambiaste `MONGO_EXPRESS_LISTEN_PORT`, abrí `localhost:${MONGO_EXPRESS_LISTEN_PORT}`.

## Archivos de la práctica

```text
data/                 CSV y JSON de entrada
00_cargar_datos.js    carga y reinicio de datos
consultas/01_...md     revisión del origen relacional
consultas/02_...md     modelado documental
consultas/03_...md     consultas básicas
consultas/04_...md     embebidos y referencias
consultas/05_...md     CRUD y validación
consultas/06_...md     agregaciones
consultas/07_...md     índices y explain
consultas/08_...md     práctica y soluciones sugeridas
```

En `mongodb`, `00_cargar_datos.js` se monta como `/scripts/00_cargar_datos.js` y `data/` como `/data/practica`, ambos en modo de solo lectura. No se montan directorios de scripts. Los datos de MongoDB persisten en `mongodb_data`.

## Reiniciar o cerrar

Para restaurar los datos iniciales sin recrear el contenedor:

```bash
docker compose exec -e MONGO_DATABASE=bdia_clase4 mongodb mongosh --quiet --username bdia_admin --password bdia_local_pass --authenticationDatabase admin /scripts/00_cargar_datos.js
```

El script elimina y recrea solo `bdia_clase4`; borra los cambios manuales de esa base.

```bash
docker compose down
```

Para borrar también el volumen local:

```bash
docker compose down -v
```

## Problemas frecuentes

- Si Compass no conecta, verificá `docker compose ps`, la URI, el puerto publicado y `authSource=admin`.
- Si cambiaste credenciales después de crear el volumen, MongoDB conserva el usuario anterior. Restaurá las credenciales originales o recreá deliberadamente el volumen con `docker compose down -v`.
- Si un puerto está ocupado, cambiá `MONGO_LISTEN_PORT` o `MONGO_EXPRESS_LISTEN_PORT` en `.env`; ambos seguirán vinculados a `127.0.0.1`.
- Con solo nueve experimentos, MongoDB puede elegir `COLLSCAN` aun después de crear un índice. Usá `explain` como evidencia, no como garantía de mejora.
