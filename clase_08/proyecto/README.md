# Espacio de experimentos de IA

Demo educativa multi-tenant, terminada como MVP de tres días, para registrar experimentos y sus resultados, trabajar con documentos privados mediante RAG y consultar datos estructurados con un asistente acotado. Está pensada para aprendizaje y ejecución local: **no es un sistema listo para producción**.

## Qué incluye el MVP

| Día | Alcance demostrable |
| --- | --- |
| 1 | Landing, registro/login, sesiones, recuperación local, espacios de trabajo, roles fijos y aislamiento con RLS. |
| 2 | Experimentos, resultados y métricas; carga privada e ingesta de PDF/TXT/MD; fragmentos y embeddings con pgvector. |
| 3 | Asistente documental, relacional y combinado; fixtures de dos tenants; pruebas de aislamiento y operaciones locales seguras. |

El recorrido feliz es: crear un espacio, registrar un experimento, cargar e ingerir un documento y consultar ambas fuentes desde el asistente.

## Arquitectura local

```text
Navegador
  ├─ landing (Astro/Nginx) ─────────────── página pública
  └─ web (React/Vite/Nginx) ───────────── frontend autenticado
                         │ cookies + CSRF
                         ▼
                    api (FastAPI)
        ┌────────────────┼─────────────────┐
        ▼                ▼                 ▼
 PostgreSQL 16       MinIO privado      Mailpit
 + pgvector + RLS    archivos originales SMTP + bandeja local
      ▲
      └─ pgAdmin (administración local de PostgreSQL)
```

| Contenedor | Responsabilidad | Límite de confianza |
| --- | --- | --- |
| `landing` | Presentación pública y acceso a la aplicación. | No recibe autoridad de tenant. |
| `web` | Interfaz autenticada. | No decide tenant, rol ni permisos; la API los deriva de la sesión. |
| `api` | Autenticación, autorización, validación, RAG y orquestación. | Única frontera confiable expuesta al navegador. |
| `db` | Datos relacionales, vectores, políticas RLS y vistas del asistente. | Separa roles de migración, ejecución y lectura del asistente. |
| `pgadmin` | Administración visual local de PostgreSQL. | Usa credenciales sintéticas de aula y persiste su configuración en un volumen propio. |
| `minio` / `minio-init` | Objetos privados y creación del bucket sin acceso anónimo. | Las claves de objeto son opacas y se entregan sólo tras autorizar en DB. |
| `mailpit` | Correo local para recuperación de cuenta. | Sólo desarrollo; su bandeja puede contener códigos temporales. |

## Inicio rápido

### Requisitos

- Docker con Docker Compose v2.
- `curl` y una shell compatible con los scripts locales.
- Puertos locales libres; los valores predeterminados están documentados en `.env.example`.

Ejecutá todo este bloque desde la raíz del repositorio:

```bash
cd clase_08/proyecto
cp .env.example .env
docker compose config --quiet
docker compose build
docker compose up -d db minio minio-init mailpit
docker compose run --rm api alembic upgrade head
docker compose up -d
docker compose ps
curl -fsS http://localhost:8000/health
```

Antes de iniciar, reemplazá en `.env` los secretos de desarrollo de ejemplo por valores locales propios. Las seis claves siguientes son credenciales **sintéticas de aula**, no cuentas personales ni credenciales de producción:

| Clave | Uso local |
| --- | --- |
| `PGADMIN_DEFAULT_EMAIL` | Usuario exclusivo para el acceso local a pgAdmin. |
| `PGADMIN_DEFAULT_PASSWORD` | Contraseña exclusiva para el acceso local a pgAdmin. |
| `ADMIN_EMAIL` | Identidad `admin` del tenant `alpha`. |
| `MEMBER_EMAIL` | Identidad `member` del tenant `alpha`. |
| `VIEWER_EMAIL` | Identidad `viewer` del tenant `alpha`. |
| `FIXTURE_PASSWORD` | Contraseña común de las seis identidades sembradas; mínimo 8 caracteres. |

Los tres correos de fixture deben ser distintos después de normalizarlos y deben pasar la misma validación de correo que aplica el backend al login; usá dominios válidos para las identidades sintéticas de aula. No publiques `.env`, estas credenciales, cookies, códigos de recuperación ni salida que los contenga. Si modificás `API_PORT`, usá ese puerto en `curl`; si cambiás URLs públicas o puertos, reconstruí `web` y `landing` porque se incorporan durante el build.

### Direcciones predeterminadas

| Servicio | Dirección |
| --- | --- |
| Landing | <http://localhost:4321> |
| Aplicación | <http://localhost:5173> |
| API / salud | <http://localhost:8000/health> |
| PostgreSQL | `localhost:5432` |
| pgAdmin | `http://localhost:${PGADMIN_PORT:-5050}` (por defecto <http://localhost:5050>) |
| MinIO API / consola | <http://localhost:9000> / <http://localhost:9001> |
| Mailpit | <http://localhost:8025> |

## Fixtures y verificación completa

El fixture es repetible y crea datos aislados para dos espacios de demostración (`alpha` y `beta`) con roles `admin`, `member` y `viewer`. Toma las cuatro credenciales sintéticas ya definidas en `.env`; `alpha` usa los correos `ADMIN_EMAIL`, `MEMBER_EMAIL` y `VIEWER_EMAIL`, mientras que `beta` conserva identidades demo deterministas. Todas usan `FIXTURE_PASSWORD`.

```bash
docker compose run --rm -T \
  -v "$PWD/scripts/seed-security-fixtures.py:/app/seed-security-fixtures.py:ro" \
  api python /app/seed-security-fixtures.py
```

El script exige las cuatro variables de fixture, correos normalizados distintos que pasen la validación del backend y una contraseña de al menos 8 caracteres; no imprime sus valores, tokens ni cookies. Para probar el login del tenant `alpha`, abrí la aplicación y escribí el valor local de `ADMIN_EMAIL`, `MEMBER_EMAIL` o `VIEWER_EMAIL` junto con `FIXTURE_PASSWORD`, sin copiarlos a comandos, documentación ni capturas. Luego ejecutá la verificación integral:

```bash
./scripts/verify-stack.sh
```

Este chequeo exige servicios saludables —incluido pgAdmin— y prueba: endpoint de salud, bucket privado, contratos relacionales/vectoriales, guard SQL, matriz de roles, aislamiento HTTP entre tenants, RLS y limpieza del contexto transaccional del pool. Conserva el origen CSRF derivado de `WEB_PORT` cuando ese puerto se personaliza.

### Acceso local a pgAdmin

Abrí `http://localhost:${PGADMIN_PORT:-5050}` (5050 si no configuraste el puerto) e iniciá sesión con los valores locales de `PGADMIN_DEFAULT_EMAIL` y `PGADMIN_DEFAULT_PASSWORD`. Para registrar PostgreSQL desde pgAdmin usá host `db`, puerto `5432` y base `student_project`; `localhost` dentro de pgAdmin apuntaría al propio contenedor. La conexión a la base requiere además un rol PostgreSQL local: no confundas esas credenciales con el login de pgAdmin ni las publiques.

## Recorrido de demo sin credenciales publicadas

Usá correos de prueba y contraseñas que controles; no los agregues al repositorio ni a capturas compartidas.

1. En `/register`, creá un espacio **A** con su propia cuenta administradora.
2. Como `admin`, abrí **Personas** y agregá una cuenta `member` y otra `viewer`.
3. En Mailpit, solicitá recuperación para cada cuenta nueva y completá su contraseña. Tratá el código del correo como secreto temporal.
4. Cerrá sesión y verificá que `member` pueda crear/editar experimentos y cargar/ingerir documentos, pero no administrar personas.
5. Verificá que `viewer` pueda consultar experimentos, descargar/buscar documentos y usar el asistente, sin mutar contenido ni administrar personas.
6. Con otros correos de prueba, repetí el registro para un espacio **B** y sus tres roles.
7. Creá nombres, resultados, métricas y documentos distintos en A y B. Al alternar sesiones, confirmá que ninguna lista, descarga, cita ni respuesta relacional cruce de espacio.

Una identidad sólo puede tener una membresía activa en este MVP; usá identidades diferentes para los dos espacios.

## Documentos y RAG

1. Como `admin` o `member`, abrí **Documentos** y subí un archivo `.pdf`, `.txt` o `.md` de hasta el límite configurado (máximo admitido: 25 MiB).
2. Elegí **Ingerir**. La API valida extensión y tipo, integridad del objeto y contenido; extrae texto, lo fragmenta y guarda embeddings de dimensión fija en pgvector.
3. Esperá el estado **Disponible**. Un error deja el documento en estado fallido y no habilita fragmentos incompletos.
4. Buscá evidencia. La respuesta devuelve fragmentos citados del tenant activo.
5. Descargá el original para comprobar que MinIO sigue privado y que el acceso pasa por autorización de la API.

Los TXT y MD deben ser UTF-8. Los PDF necesitan texto extraíble; no hay OCR. La ingesta es síncrona y adecuada sólo para la demostración local.

## Modos del asistente

| Modo | Comportamiento actual |
| --- | --- |
| **Documentos** | Recupera fragmentos de documentos ya ingeridos y devuelve citas. |
| **Datos relacionales** | Consulta vistas curadas de experimentos, resultados y métricas. |
| **Combinado** | Intenta ambas fuentes y marca una respuesta parcial si sólo una está disponible. |
| **Automático** | En este MVP se resuelve de forma determinista como **Combinado**; no clasifica intención con un modelo externo. |

El SQL del asistente no se ejecuta como usuario de escritura: acepta una gramática pequeña de un único `SELECT`, sólo sobre vistas permitidas y columnas conocidas, en transacción de sólo lectura, con timeout y límites de filas/tamaño. El tenant y el usuario se toman de la sesión validada, nunca del prompt ni del frontend.

## Activar OpenRouter y embeddings

El asistente usa OpenRouter en tiempo de ejecución. Definí `OPENROUTER_API_KEY` sólo en tu entorno local y, opcionalmente, `OPENROUTER_MODEL` (por defecto `openai/gpt-4o-mini`) antes de iniciar `api`. Una clave ausente, vacía o de placeholder falla de forma cerrada: la API responde 503 y no intenta conectarse. `LocalAssistantProvider` queda reservado como doble determinista de pruebas; los embeddings continúan usando el adaptador local.

> **Privacidad y costo:** las preguntas y una muestra acotada de fragmentos/filas se envían a un servicio externo. No uses datos personales, secretos ni contenido que no pueda salir del entorno. El proveedor puede cobrar según el modelo y los tokens. Cada generación realiza un solo intento, sin reintentos automáticos, para evitar costos duplicados.

La respuesta se limita y el contexto elimina identificadores de tenant, claves de objeto, sesión/autorización, errores internos y detalles del proveedor. Aun así, revisá las políticas del modelo elegido: la redacción automática no sustituye una clasificación de datos. Nunca imprimas ni publiques la clave, headers, configuración volcada, cuerpos crudos o trazas completas.

Si el asistente devuelve 503, verificá localmente que ambas variables estén definidas y que el modelo exista; ante timeout, 401, 429 o 5xx corregí conectividad, autorización, cuota o disponibilidad y repetí manualmente. La API oculta cuerpos y detalles internos deliberadamente: diagnosticá con estado HTTP sanitizado, sin copiar secretos a logs o reportes.

## Límites de confianza y aislamiento

| Superficie | Garantía del MVP |
| --- | --- |
| Relacional | Todas las entidades de negocio llevan tenant; la API fija `app.user_id` y `app.tenant_id` por transacción y PostgreSQL aplica RLS. |
| Vector/RAG | Documentos, fragmentos y embeddings se enlazan por tenant; la recuperación filtra explícitamente y también queda bajo RLS. |
| Objetos | Bucket sin listado anónimo, claves opacas prefijadas por tenant y capacidad de lectura/escritura creada sólo después de autorizar en DB. |
| SQL del asistente | Rol DB separado y de sólo lectura, vistas curadas, parser de allow-list y cotas duras; no acepta SQL arbitrario ni identificadores del prompt. |
| Sesión y CSRF | Cookie de sesión opaca con hash persistido; mutaciones requieren cookie/header CSRF coincidentes y origen permitido. Logout revoca la sesión. |
| Roles | `admin` administra personas; `admin` y `member` mutan trabajo/documentos; `viewer` consulta. El backend vuelve a comprobar el rol en cada frontera. |

Estas capas son complementarias: los filtros de aplicación no sustituyen RLS, y conocer una clave de objeto o un identificador no concede acceso.

## Reutilización selectiva y material fuente

La implementación clasifica la reutilización así:

- **Reutilizado como referencia:** conceptos docentes, vocabulario y patrones generales.
- **Adaptado dentro del proyecto:** estructura visual y componentes compatibles con este demo.
- **Implementado específicamente:** modelo multi-tenant, migraciones/RLS, API, RAG, guard SQL, fixtures y operaciones Compose.
- **No incorporado:** ejemplos que ampliarían el alcance o debilitarían los límites anteriores.

`material_desarrollo/**` es material de consulta inmutable: este proyecto no lo modifica, mueve, genera ni usa como destino de herramientas. Todo artefacto ejecutable del demo vive bajo `clase_08/proyecto/`.

## Capacidades diferidas y limitaciones conocidas

No forman parte de este MVP:

- invitaciones por correo y OAuth;
- OCR y extracción avanzada de imágenes;
- colas, workers e ingesta asíncrona;
- roles personalizados o permisos configurables;
- streaming de respuestas e historial conversacional;
- dashboards avanzados;
- despliegue productivo, alta disponibilidad y observabilidad operacional;
- múltiples proveedores o selección dinámica de modelos;
- ingesta no trivial de PNG/JPEG/CSV/JSON.

También se asume desarrollo local, una membresía activa por identidad, Mailpit como correo no entregable y respuestas del asistente basadas sólo en evidencia acotada disponible.

## Operación segura

### Detener sin borrar datos

```bash
docker compose down
```

### Reset local guardado

```bash
./scripts/reset-local.sh
```

El script se niega a operar fuera de `APP_ENV=development`, rechaza hosts Docker remotos, verifica el nombre exacto `bdia-project`, muestra los volúmenes con esa etiqueta Compose y exige escribir `RESET bdia-project`. Borra únicamente contenedores, red y volúmenes nombrados de este proyecto, incluido el volumen dedicado de pgAdmin; la pérdida de datos es irreversible.

No uses `docker compose down -v`, `docker volume prune` ni `docker system prune` como atajos.

## Diagnóstico acotado

1. Revisá estado y salud sin volcar configuración:

   ```bash
   docker compose ps
   curl -fsS http://localhost:8000/health
   ```

2. Consultá sólo el servicio afectado y una ventana corta de logs:

   ```bash
   docker compose logs --tail=100 api
   docker compose logs --tail=100 web
   docker compose logs --tail=100 db
   docker compose logs --tail=100 minio
   docker compose logs --tail=100 mailpit
   ```

3. Para una migración pendiente, repetí el comando idempotente:

   ```bash
   docker compose run --rm api alembic upgrade head
   ```

4. Si cambiaste puertos o URLs públicas, corregí `.env` y reconstruí sólo las interfaces:

   ```bash
   docker compose up --build -d web landing
   ```

5. Si falla ingesta, comprobá salud de `api`, `db` y `minio`, el formato permitido y el estado del documento. Si falla correo, revisá `mailpit`. No pegues `.env`, headers, cookies, URLs con tokens ni trazas completas en reportes; compartí sólo el mensaje sanitizado, servicio y paso reproducible.

Si `./scripts/verify-stack.sh` falla, seguí el servicio que indica el error; no desactives RLS, CSRF, validaciones ni límites para “hacer pasar” la demo.
