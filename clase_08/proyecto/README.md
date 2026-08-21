# Espacio de experimentos de IA

Aplicación educativa multi-tenant para registrar experimentos de inteligencia artificial, relacionar datasets, modelos, resultados y métricas, consultar documentos mediante embeddings/RAG y analizar datos estructurados con Text-to-SQL de solo lectura.

La landing pública, el frontend React autenticado, la API FastAPI, PostgreSQL con pgvector, MinIO y Mailpit se ejecutan localmente mediante Docker Compose.

## Inicio rápido

### Requisitos

- Docker con Docker Compose v2.
- Los puertos configurados en `.env` deben estar disponibles en la computadora.

### 1. Preparar la configuración

Desde la raíz del repositorio:

```bash
cd clase_08/proyecto
cp .env.example .env
```

El archivo `.env` es local. Podés modificar sus puertos y credenciales de desarrollo sin cambiar `compose.yaml`.

### 2. Validar Docker Compose

```bash
docker compose config
```

El comando debe finalizar sin errores.

### 3. Iniciar la infraestructura

```bash
docker compose up -d db minio minio-init mailpit
```

Comprobá el estado:

```bash
docker compose ps
```

Esperá hasta que PostgreSQL, MinIO y Mailpit estén saludables. `minio-init` debe finalizar correctamente y quedar en estado `Exited (0)`.

### 4. Aplicar las migraciones

```bash
docker compose run --rm api alembic upgrade head
```

Este paso crea el esquema, los roles y las políticas RLS necesarias para ejecutar la aplicación.

> La aplicación no incluye usuarios ni credenciales predeterminadas. Después de iniciar el stack, cada estudiante debe crear el primer usuario administrador desde `/register`.

### 5. Construir e iniciar la aplicación

```bash
docker compose up --build -d
docker compose ps
```

Esperá hasta que `landing`, `web`, `api`, `db`, `minio` y `mailpit` aparezcan como saludables.

### 6. Verificar la API

```bash
curl http://localhost:8000/health
```

Si cambiaste `API_PORT`, reemplazá `8000` por el puerto configurado en `.env`.

## Servicios locales

`.env.example` contiene los puertos estándar:

| Servicio | Dirección predeterminada | Variable |
| --- | --- | --- |
| Landing pública | <http://localhost:4321> | `LANDING_PORT=4321` |
| Aplicación autenticada | <http://localhost:5173> | `WEB_PORT=5173` |
| API | <http://localhost:8000> | `API_PORT=8000` |
| PostgreSQL | `localhost:5432` | `POSTGRES_PORT=5432` |
| API de MinIO | <http://localhost:9000> | `MINIO_API_PORT=9000` |
| Consola de MinIO | <http://localhost:9001> | `MINIO_CONSOLE_PORT=9001` |
| SMTP de Mailpit | `localhost:1025` | `MAILPIT_SMTP_PORT=1025` |
| Bandeja de Mailpit | <http://localhost:8025> | `MAILPIT_UI_PORT=8025` |

## Cambiar puertos ocupados

Modificá únicamente los valores del lado del host en `.env`. Los puertos internos de los contenedores no cambian.

Ejemplo:

```env
LANDING_PORT=14321
WEB_PORT=15173
API_PORT=18000
POSTGRES_PORT=15432
MINIO_API_PORT=19000
MINIO_CONSOLE_PORT=19001
MAILPIT_SMTP_PORT=11025
MAILPIT_UI_PORT=18025
```

Luego reconstruí las imágenes porque Vite incorpora las URLs públicas durante el build:

```bash
docker compose up --build -d
```

Compose deriva automáticamente:

- La URL de la API utilizada por el frontend desde `API_PORT`.
- La URL de la landing utilizada por el frontend desde `LANDING_PORT`.
- La URL del frontend utilizada por la landing desde `WEB_PORT`.
- Los orígenes CORS permitidos desde `WEB_PORT` y `LANDING_PORT`.

## Recorrido manual de prueba

### 1. Landing pública

1. Abrí la URL de la landing.
2. Probá la navegación de escritorio y móvil.
3. Cambiá entre tema claro y oscuro.
4. Recargá la página y verificá que el tema elegido se conserve.
5. Presioná **Acceder al sistema** y confirmá que se abra el login.
6. Revisá los enlaces **Crear espacio** e **Ingresar**.

### 2. Registro y sesión

1. Abrí `/register` en la aplicación autenticada.
2. Ingresá el nombre del equipo, un correo electrónico y una contraseña.
3. Confirmá que el registro abra el panel protegido.
4. Cerrá la sesión.
5. Volvé a ingresar desde `/login`.
6. Recargá el navegador y verificá que la sesión permanezca activa.
7. Usá **Volver al inicio** para regresar a la landing.

El registro crea un espacio de trabajo y una membresía activa con rol administrador. Durante el login, el backend resuelve automáticamente ese espacio; el usuario no debe ingresar ni seleccionar UUIDs de tenants.

### 3. Personas y roles

1. Ingresá como administrador del espacio.
2. Abrí **Personas**.
3. Agregá una persona con rol `member` o `viewer`.
4. Confirmá que el sistema no le solicite al administrador definir la contraseña de esa persona.

Los roles disponibles son:

| Rol | Uso esperado |
| --- | --- |
| `admin` | Gestiona las personas del espacio. |
| `member` | Participa del trabajo del espacio. |
| `viewer` | Accede en modo de consulta. |

### 4. Configurar contraseña mediante Mailpit

1. Abrí la bandeja de Mailpit.
2. Solicitá recuperación de cuenta para la persona creada.
3. Abrí el correo recibido en Mailpit.
4. Copiá el código de recuperación.
5. Usá `/recovery/confirm` para definir la contraseña inicial.
6. Ingresá con la nueva cuenta.
7. Confirmá que un usuario `viewer` no pueda administrar personas.

### 5. Navegación protegida

Confirmá que la aplicación muestre:

- **Panel**.
- **Personas**, cuando la sesión tiene capacidad para administrarlas.
- **Experimentos**.
- **Documentos**.
- **Asistente**.

Actualmente, Experimentos, Documentos y Asistente presentan la navegación y el diseño base. Su funcionalidad se incorpora en las siguientes entregas.

## Verificaciones automatizadas

Estas verificaciones son opcionales para probar manualmente la aplicación, pero son necesarias al modificar el código.

### Frontend

```bash
cd clase_08/proyecto/frontend
npm install
npm test
npm run typecheck
npm run lint
npm run build
```

### Landing

```bash
cd clase_08/proyecto/landing
npm install
npm test
npm run check
npm run build
npm audit
```

### Backend

Si todavía no existe el entorno virtual:

```bash
cd clase_08/proyecto/backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Ejecutá las pruebas y verificaciones:

```bash
.venv/bin/python -m unittest -v \
  tests/test_foundation.py \
  tests/test_identity_security.py \
  tests/test_tenant_context.py \
  tests/test_identity_http.py

.venv/bin/python -m compileall -q app migrations
npx --no-install pyright --project pyrightconfig.json
```

`test_identity_http.py` se omite cuando no recibe las URLs de un entorno Compose aislado. El recorrido manual anterior verifica el flujo público de identidad contra el stack local.

### Docker Compose

```bash
cd clase_08/proyecto
docker compose config
docker compose ps
```

## Diagnóstico de problemas

### Docker no puede publicar un puerto

Si aparece un error como `failed to bind host port`, otro proceso está utilizando ese puerto. Identificalo con:

```bash
ss -ltnp '( sport = :9000 or sport = :9001 )'
```

La opción recomendada es cambiar solamente los puertos del host en `.env`. Por ejemplo:

```env
MINIO_API_PORT=19000
MINIO_CONSOLE_PORT=19001
```

Después recreá los contenedores sin borrar los volúmenes:

```bash
docker compose down --remove-orphans
docker compose up -d
docker compose ps
```

No uses `-v`: los datos de PostgreSQL y MinIO deben conservarse. Si MinIO no pudo conectarse a la red durante el primer intento, `minio-init` también puede fallar con `lookup minio ... server misbehaving`; recrear el stack después de liberar o cambiar los puertos corrige ambas consecuencias.

### Consultar logs

```bash
docker compose logs -f api
docker compose logs -f web
docker compose logs -f landing
docker compose logs -f db
docker compose logs -f mailpit
```

Presioná `Ctrl+C` para dejar de seguir los logs; los contenedores continuarán ejecutándose.

### Volver a aplicar migraciones

```bash
docker compose run --rm api alembic upgrade head
```

### El navegador conserva una versión anterior

Reconstruí la imagen correspondiente:

```bash
docker compose up --build -d web landing
```

Después recargá el navegador sin caché con `Ctrl+Shift+R`.

### El frontend utiliza un puerto anterior de la API

Vite incorpora la URL durante la construcción. Reconstruí `web`:

```bash
docker compose up --build -d web
```

## Detener o reiniciar el entorno

### Detener sin borrar datos

```bash
docker compose down
```

Los volúmenes de PostgreSQL y MinIO se conservan.

### Borrar completamente los datos locales

```bash
docker compose down -v --remove-orphans
```

> **Advertencia:** este comando elimina permanentemente la base de datos y los archivos almacenados localmente por este proyecto.
