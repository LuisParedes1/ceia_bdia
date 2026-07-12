# 07. Índices y `explain`

Abrí el **shell integrado de MongoDB Compass** y ejecutá los bloques **en orden** sobre `bdia_clase4`. En cada plan expandí `queryPlanner.winningPlan` y `executionStats`.

## Plan sin índice específico

**Objetivo:** medir una consulta antes de crear el índice.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
if (practica.experimentos.getIndexes().some((indice) => indice.name === "idx_propietario_finalizado")) {
  practica.experimentos.dropIndex("idx_propietario_finalizado");
}
practica.experimentos.find(
  {finalizado: false, "dataset.propietario.usuario_id": 6},
).explain("executionStats");
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| `getIndexes()` | Método de colección que devuelve un array con las definiciones de sus índices. | Permite comprobar si existe el índice del ejercicio. |
| `.some((indice) => ...)` | Método de arrays de JavaScript que devuelve `true` si al menos un elemento cumple la condición. | Decide si es necesario ejecutar `dropIndex`. |
| `if (...) { ... }` | Estructura de control de JavaScript que ejecuta el bloque solo cuando la condición es verdadera. | Evita un error al intentar eliminar un índice inexistente. |
| `dropIndex(nombre)` | Elimina de la colección el índice indicado y devuelve un documento de respuesta del comando. | Restablece el escenario inicial sin el índice específico. |
| `.explain("executionStats")` | En lugar de devolver los documentos de `find`, ejecuta la consulta y retorna un **plan de ejecución** con la estrategia elegida y estadísticas reales. | Establece la medición base antes de crear el índice. |
| `queryPlanner.winningPlan` | Sección del plan que describe la estrategia ganadora, por ejemplo `COLLSCAN` o `IXSCAN`. | Permite identificar cómo resolvió MongoDB el filtro. |
| `executionStats.totalDocsExamined` / `nReturned` | Indican cuántos documentos se examinaron y cuántos se devolvieron. | Permiten comparar trabajo realizado frente a resultados obtenidos. |

**Qué hace:** garantiza que el índice del ejercicio no exista y obtiene plan más estadísticas reales.

**Observá:** registrá la etapa ganadora, `totalDocsExamined` y `nReturned`.

## Índice compuesto

**Objetivo:** alinear un índice con los dos predicados de igualdad.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.experimentos.createIndex(
  {"dataset.propietario.usuario_id": 1, finalizado: 1},
  {name: "idx_propietario_finalizado"},
);
practica.experimentos.find(
  {finalizado: false, "dataset.propietario.usuario_id": 6},
).explain("executionStats");
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| `createIndex(claves, opciones)` | Método de colección que crea un índice y devuelve su nombre. El primer argumento define campos y orden; el segundo configura opciones. | Crea el índice compuesto que luego puede usar la consulta. |
| Índice compuesto | Indexa más de un campo en el orden declarado. Los valores `1` indican orden ascendente del índice. | Cubre los dos predicados de igualdad sobre propietario y estado. |
| `{name: "..."}` | Asigna un nombre explícito al índice. | Facilita identificarlo y eliminarlo de forma reproducible. |
| Segundo `explain("executionStats")` | Vuelve a producir un plan de ejecución para la misma consulta, ahora con el índice disponible. | Permite comparar evidencia sin asumir que el optimizador elegirá el índice. |

**Qué hace:** crea el índice y vuelve a medir la misma consulta.

**Observá:** compará el plan y documentos examinados. Con solo nueve documentos, el optimizador puede preferir `COLLSCAN`; eso no invalida el índice.

**Comparación con SQL:** como en PostgreSQL, el índice favorece ciertos accesos pero agrega almacenamiento y costo de escritura.

## Índice multikey

**Objetivo:** indexar referencias ubicadas dentro de un array.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.experimentos.createIndex(
  {"ejecuciones.modelo_id": 1},
  {name: "idx_ejecuciones_modelo_id"},
);
practica.experimentos.find(
  {"ejecuciones.modelo_id": "mod-006"},
).explain("executionStats");
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| Índice sobre `ejecuciones.modelo_id` | Al indexar una ruta cuyos valores están dentro de un array, MongoDB crea automáticamente un índice **multikey**, con entradas para sus elementos. | Hace indexables las referencias `modelo_id` de las ejecuciones. |
| `isMultiKey` | Propiedad del plan que informa si el índice involucrado es multikey. | Permite verificar la naturaleza del índice creado. |
| `explain` | Devuelve el plan, no los documentos coincidentes. | Comprueba si el índice puede participar y cuál estrategia elige el optimizador. |

**Qué hace:** MongoDB convierte automáticamente el índice del campo de array en multikey.

**Observá:** buscá `isMultiKey: true` en el plan asociado al índice, aunque el optimizador no lo elija por el tamaño de la colección.

## Inventario final

**Objetivo:** revisar los índices disponibles.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.experimentos.getIndexes();
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| `getIndexes()` | Devuelve un array de documentos con nombre, claves y propiedades de cada índice. | Revisa juntos el índice automático `_id_` y los dos creados en el ejercicio. |

**Qué hace:** lista definición, nombre y propiedades de cada índice.

**Observá:** deben figurar `_id_`, `idx_propietario_finalizado` e `idx_ejecuciones_modelo_id`.
