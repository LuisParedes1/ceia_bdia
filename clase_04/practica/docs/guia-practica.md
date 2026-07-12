# Guía práctica MongoDB y Compass

El recorrido de la clase es: levantar Compose, cargar el estado inicial con el script `00`, conectarse desde Compass y resolver en orden `consultas/01..08`.

## 1. Preparar el entorno

Instalá Docker, Git y MongoDB Compass. Compass es un cliente externo: no se instala con este Compose.

Desde `clase_04/practica`, creá la configuración local:

```bash
cp .env.example .env
```

En Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

## 2. Levantar los servicios

```bash
docker compose up -d --wait
docker compose ps
```

Esperá hasta que `mongodb` figure como saludable. El Compose levanta MongoDB y Mongo Express; este último es opcional.

## 3. Cargar o reiniciar los datos

El archivo `00_cargar_datos.js` está en la raíz de la práctica y Compose lo monta en `/scripts/00_cargar_datos.js`. Ejecutalo completo dentro del contenedor:

```bash
docker compose exec -e MONGO_DATABASE=bdia_clase4 mongodb mongosh --quiet --username bdia_admin --password bdia_local_pass --authenticationDatabase admin /scripts/00_cargar_datos.js
```

Debe finalizar con `Carga completa y consistente en la base bdia_clase4.`. Este es el único script obligatorio que se ejecuta mediante Docker: necesita leer los CSV y JSON montados dentro del contenedor y recrea solamente `bdia_clase4`.

## 4. Conectar MongoDB Compass

Creá una conexión con:

```text
mongodb://bdia_admin:bdia_local_pass@localhost:27017/?authSource=admin
```

Si modificaste `.env`, ajustá credenciales y `MONGO_LISTEN_PORT`. Seleccioná la base `bdia_clase4`.

## 5. Trabajar los ejercicios

Abrí los archivos Markdown en el editor o navegador y recorrélos en orden:

| Ejercicio                                                           | Práctica                                       |
| ------------------------------------------------------------------- | ---------------------------------------------- |
| [`01`](../consultas/01_revisar_origen_relacional.md)                | Origen normalizado y `$lookup`.                |
| [`02`](../consultas/02_modelar_documentos.md)                       | Embedding, referencias y patrones de acceso.   |
| [`03`](../consultas/03_consultas_basicas.md)                        | Filtros, proyección, orden y arrays.           |
| [`04`](../consultas/04_embebidos_y_referencias.md)                  | `$elemMatch`, `$unwind` y `$lookup`.           |
| [`05`](../consultas/05_inserciones_actualizaciones_y_validacion.md) | CRUD, arrays, validator y errores esperados.   |
| [`06`](../consultas/06_agregaciones.md)                             | Agrupaciones, ventanas y campos calculados.    |
| [`07`](../consultas/07_indices_y_explain.md)                        | Índices y planes de ejecución.                 |
| [`08`](../consultas/08_practica.md)                                 | Consignas integradoras y soluciones sugeridas. |

Cada archivo indica dónde pegar el bloque, qué hace y qué resultado observar. Copiá y ejecutá los bloques en el **shell integrado de Compass**; cuando se indique, usá también las pestañas **Aggregations**, **Indexes** o **Validation**.

Compass no abre ni ejecuta archivos del contenedor y no puede acceder a `/scripts`. Esa ruta pertenece al servicio `mongodb`; Compose monta allí, en modo de solo lectura, el archivo raíz `00_cargar_datos.js`.

## 6. Usar Mongo Express como visor opcional

Abrí <http://localhost:8081> con usuario `admin` y contraseña `admin_local`, salvo que hayas cambiado `.env`.

Mongo Express permite recorrer bases, colecciones y documentos. No reemplaza el shell ni las herramientas de consulta de Compass.

## 7. Recuperar el estado inicial

Si un ejercicio quedó incompleto o querés eliminar cambios, repetí el comando del script `00`:

```bash
docker compose exec -e MONGO_DATABASE=bdia_clase4 mongodb mongosh --quiet --username bdia_admin --password bdia_local_pass --authenticationDatabase admin /scripts/00_cargar_datos.js
```

La recarga elimina y vuelve a crear únicamente `bdia_clase4`.

## 8. Detener el entorno

Para conservar el volumen:

```bash
docker compose down
```

No uses `-v` salvo que quieras borrar deliberadamente todos los datos persistidos de esta práctica.

## Problemas frecuentes

- Si Compass no conecta, verificá `docker compose ps`, la URI, el puerto publicado y `authSource=admin`.
- Si modificaste credenciales después de crear el volumen, MongoDB conserva el usuario anterior. Recuperá las credenciales originales o recreá deliberadamente el volumen.
- Si un puerto está ocupado, cambiá `MONGO_LISTEN_PORT` o `MONGO_EXPRESS_LISTEN_PORT` en `.env`.
- Con nueve experimentos, MongoDB puede elegir `COLLSCAN` aunque exista un índice. Compará evidencia de `explain`; no presupongas una mejora.
