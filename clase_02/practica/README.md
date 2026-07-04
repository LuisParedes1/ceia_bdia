# BDIA - Práctica PostgreSQL y pgAdmin con Docker

Este repositorio prepara un entorno local para una práctica de Bases de Datos para Inteligencia Artificial. La clase trabaja únicamente con PostgreSQL como motor de base de datos y pgAdmin como interfaz web de administración.

## Ruta rápida

1. Instalá Docker Desktop y Git según tu sistema operativo.
2. Creá tu archivo `.env` a partir de `.env.example`.
3. Levantá los servicios:

```bash
docker compose up -d
```

Docker compose se baja las imagenes de Dockerhub: [pgadmin4](https://hub.docker.com/r/dpage/pgadmin4) & [postgres](https://hub.docker.com/_/postgres)


4. Entrá a pgAdmin en <http://localhost:8080>.
5. Conectate al servidor PostgreSQL usando el host `postgres`.
   - Register server
   - Connection tab
      - host: postgres
      - port: POSTGRES_LISTEN_PORT
      - Maintenance database: POSTGRES_DB
      - Username: POSTGRES_USER
      - Password: POSTGRES_PASSWORD

-> Usar las credenciales dentro de `.env` <-

6. Ejecutá los scripts de la carpeta `sql/` desde **Query Tool**.

## Objetivo de la práctica

Construir un entorno local y reproducible para:

- Crear tablas en PostgreSQL.
- Insertar datos de práctica.
- Ejecutar consultas SQL.
- Validar restricciones del modelo.
- Administrar la base desde pgAdmin.

## Servicios incluidos

| Servicio | Uso | Acceso |
|----------|-----|--------|
| PostgreSQL | Motor de base de datos relacional. | Puerto local `POSTGRES_LISTEN_PORT` (por defecto `5432`). |
| pgAdmin 4 | Interfaz web para administrar PostgreSQL y ejecutar SQL. | <http://localhost:PGADMIN_LISTEN_PORT> (por defecto `8080`). |

## Requisitos previos en Windows

- Windows 10/11.
- Docker Desktop.
- WSL2.
- Git.
- Navegador web.

### Instalar herramientas en Windows

1. Instalá Git desde <https://git-scm.com/download/win>.
2. Instalá Docker Desktop desde <https://www.docker.com/products/docker-desktop/>.
3. Abrí Docker Desktop y aceptá la configuración con WSL2 si la solicita.
4. Verificá la instalación desde PowerShell:

```powershell
docker --version
docker compose version
```

## Requisitos previos en macOS

- macOS actualizado.
- Docker Desktop para Mac.
- Git.
- Navegador web.

### Instalar herramientas en macOS

1. Instalá Git con Xcode Command Line Tools:

```bash
xcode-select --install
```

También podés instalarlo con Homebrew:

```bash
brew install git
```

2. Instalá Docker Desktop desde <https://www.docker.com/products/docker-desktop/>.
3. Abrí Docker Desktop.
4. Verificá la instalación:

```bash
docker --version
docker compose version
```

## Clonar el repositorio

```bash
git clone URL_DEL_REPOSITORIO
cd NOMBRE_DEL_REPOSITORIO
```

## Configuración del entorno

El archivo `.env` define las credenciales usadas por Docker Compose.

Como buena práctica, el repositorio incluye `.env.example` como plantilla. Cada persona debe crear su propio `.env` local:

```bash
cp .env.example .env
```

En Windows PowerShell podés usar:

```powershell
Copy-Item .env.example .env
```

La plantilla contiene:

```env
POSTGRES_DB=bdia_clase2
POSTGRES_USER=bdia_user
POSTGRES_PASSWORD=bdia_pass

POSTGRES_LISTEN_PORT=5432

PGADMIN_DEFAULT_EMAIL=admin@bdia.com
PGADMIN_DEFAULT_PASSWORD=admin

PGADMIN_LISTEN_PORT=8080
```

Estas credenciales son para práctica local. No deben usarse en producción.

`POSTGRES_LISTEN_PORT` y `PGADMIN_LISTEN_PORT` definen los puertos locales (host) contra los que se accede a cada servicio. Los puertos internos dentro de la red de Docker no cambian: PostgreSQL sigue escuchando en `5432` y pgAdmin en `80`.

## Levantar los servicios

```bash
docker compose up -d
```

Este comando levanta PostgreSQL y pgAdmin.

## Ver contenedores

```bash
docker compose ps
```

## Acceder a pgAdmin

Abrí el navegador en:

<http://localhost:8080>

(o el puerto que hayas definido en `PGADMIN_LISTEN_PORT`).

Credenciales:

- Usuario: `admin@bdia.com`
- Contraseña: `admin`

## Crear la conexión a PostgreSQL en pgAdmin

1. En pgAdmin, seleccioná **Servers > Register > Server**.
2. En la pestaña **General**:
   - **Name**: `BDIA PostgreSQL`
3. En la pestaña **Connection**:
   - **Host name/address**: `postgres`
   - **Port**: `5432`
   - **Maintenance database**: `bdia_clase2`
   - **Username**: `bdia_user`
   - **Password**: `bdia_pass`
4. Guardá la conexión.

> Dentro de Docker, el host correcto es `postgres`, no `localhost`.

## Ejecutar scripts SQL

Los scripts están en la carpeta `sql/` y se ejecutan desde **Query Tool** de pgAdmin.

Orden sugerido:

1. `01_crear_tablas.sql`
2. `02_insertar_datos.sql`
3. `03_consultas_basicas.sql`
4. `04_validar_restricciones.sql`

## Detener el entorno

Para detener los contenedores sin borrar datos:

```bash
docker compose down
```

Para detener los contenedores y borrar los volúmenes persistentes:

```bash
docker compose down -v
```

> Advertencia: `docker compose down -v` elimina los datos guardados en PostgreSQL y pgAdmin.

## Problemas frecuentes

### El puerto 5432 está ocupado

Cambiá `POSTGRES_LISTEN_PORT` en tu `.env`, por ejemplo:

```env
POSTGRES_LISTEN_PORT=5433
```

Reiniciá los servicios (`docker compose up -d`) y conectate desde herramientas locales usando el puerto `5433`. Dentro de Docker, PostgreSQL sigue escuchando en `5432`.

Si el puerto ocupado es el de pgAdmin, cambiá `PGADMIN_LISTEN_PORT` de la misma forma.

### No puedo entrar a pgAdmin

Verificá que el contenedor esté levantado:

```bash
docker compose ps
```

### pgAdmin no conecta con PostgreSQL

Revisá que el host sea `postgres`, no `localhost`.

### Docker no está iniciado

Abrí Docker Desktop y esperá a que termine de iniciar.

## Estructura del proyecto

```text
.
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── sql/
│   ├── 01_crear_tablas.sql
│   ├── 02_insertar_datos.sql
│   ├── 03_consultas_basicas.sql
│   └── 04_validar_restricciones.sql
└── docs/
    └── guia-practica.md
```
