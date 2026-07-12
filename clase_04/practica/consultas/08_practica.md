# 08. Práctica integradora

Abrí el **shell integrado de MongoDB Compass**, seleccioná `bdia_clase4` y escribí tus consultas. Podés usar esta comprobación inicial:

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.experimentos.find({}, {_id: 1, nombre: 1, finalizado: 1}).sort({_id: 1}).toArray();
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta comprobación |
|---|---|---|
| `find({}, proyección)` | El filtro vacío `{}` acepta todos los documentos y el segundo argumento limita los campos devueltos. | Prepara una revisión breve del estado inicial. |
| `.sort({_id: 1}).toArray()` | Ordena el cursor por `_id` ascendente y lo materializa como array. | Permite confirmar de forma estable que hay nueve experimentos antes de resolver. |

**Observá:** deben aparecer nueve experimentos. Las consignas no modifican los experimentos. El ejercicio 5 crea un índice y la prueba opcional del ejercicio 6 crea una colección separada con métricas de ejemplo.

## Consignas

1. Listá los experimentos no finalizados con nombre del experimento, nombre del dataset, propietario y nombres de modelos. Proyectá solo esos datos.
2. Encontrá ejecuciones de clasificación cuyo `class_weight` sea `balanced`. Asegurate de que ambas condiciones correspondan al mismo elemento del array.
3. Calculá el accuracy promedio por propietario. Conservá solo propietarios con al menos dos experimentos medidos y ordená el promedio de mayor a menor.
4. Para cada modelo usado por `exp-006`, recuperá con `$lookup` su versión actual. Explicá cuándo alcanza el snapshot embebido y cuándo necesitás consultar `modelos`.
5. Diseñá un índice para consultas por `dataset.tipo_fuente` y fecha descendente. Crealo y compará la consulta con `explain("executionStats")`; no afirmes una mejora sin medir.
6. Si cada experimento produjera millones de métricas temporales, proponé un modelo alternativo. Considerá el límite de documento de 16 MB, la frecuencia de escritura y las consultas por rango temporal.

## Soluciones sugeridas

Intentá resolver todas las consignas antes de desplegar esta sección.

<details>
<summary>Mostrar soluciones</summary>

### 1. Pendientes con contexto

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.experimentos.aggregate([
  {$match: {finalizado: false}},
  {$project: {
    _id: 0,
    experimento: "$nombre",
    dataset: "$dataset.nombre",
    propietario: "$dataset.propietario.nombre",
    modelos: "$ejecuciones.modelo_nombre",
  }},
  {$sort: {experimento: 1}},
]).toArray();
```

#### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta solución |
|---|---|---|
| `$match` | Filtra la entrada de la pipeline. | Conserva únicamente experimentos con `finalizado: false`. |
| `$project` con rutas de arrays | Al proyectar `"$ejecuciones.modelo_nombre"`, conserva como array los valores de esa ruta. | Devuelve los nombres de modelos sin desarmar `ejecuciones`. |
| `$sort` | Ordena la salida de agregación. | Presenta los pendientes alfabéticamente por experimento. |

**Resultado esperado:** solo experimentos pendientes; `modelos` permanece como array.

### 2. Condiciones en la misma ejecución

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.experimentos.find(
  {ejecuciones: {$elemMatch: {tipo_modelo: "Clasificación", "parametros.class_weight": "balanced"}}},
  {_id: 1, nombre: 1, ejecuciones: {$elemMatch: {tipo_modelo: "Clasificación", "parametros.class_weight": "balanced"}}},
).toArray();
```

#### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta solución |
|---|---|---|
| `$elemMatch` en filtro | Exige que las dos condiciones coincidan en el mismo elemento del array. | Selecciona una ejecución que sea de clasificación y use peso balanceado. |
| `$elemMatch` en proyección | Conserva el primer elemento que cumple esas mismas condiciones. | Evita mostrar ejecuciones ajenas a la consigna. |

**Resultado esperado:** cada elemento proyectado cumple ambas condiciones; `$elemMatch` evita cruces entre ejecuciones.

### 3. Promedio por propietario

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.experimentos.aggregate([
  {$match: {"metricas.accuracy": {$exists: true}}},
  {$group: {
    _id: "$dataset.propietario.usuario_id",
    propietario: {$first: "$dataset.propietario.nombre"},
    cantidad: {$sum: 1},
    accuracy_promedio: {$avg: "$metricas.accuracy"},
  }},
  {$match: {cantidad: {$gte: 2}}},
  {$sort: {accuracy_promedio: -1}},
  {$project: {_id: 0, propietario: 1, cantidad: 1, accuracy_promedio: 1}},
]).toArray();
```

#### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta solución |
|---|---|---|
| `$group` | Agrupa por `usuario_id` y calcula campos mediante acumuladores. | Produce un resumen por propietario. |
| `$first` | Acumulador que conserva el valor del primer documento que llega a cada grupo. | Asocia el nombre del propietario con su identificador de agrupación. |
| `$sum: 1` / `$avg` | Cuentan documentos y calculan el promedio numérico del grupo. | Obtienen `cantidad` y `accuracy_promedio`. |
| Segundo `$match` | Filtra documentos ya agrupados; `$gte: 2` significa “mayor o igual que dos”. | Descarta propietarios con menos de dos experimentos medidos. |
| `$project` | Elimina el `_id` técnico de agrupación y conserva los campos del resumen. | Da forma a la salida final. |

**Resultado esperado:** solo propietarios con al menos dos experimentos que tengan `accuracy`.

### 4. Referencia al modelo actual

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.experimentos.aggregate([
  {$match: {_id: "exp-006"}},
  {$unwind: "$ejecuciones"},
  {$lookup: {from: "modelos", localField: "ejecuciones.modelo_id", foreignField: "_id", as: "modelo"}},
  {$unwind: "$modelo"},
  {$project: {_id: 0, snapshot: "$ejecuciones.modelo_nombre", modelo_id: "$modelo._id", version_actual: "$modelo.version"}},
]).toArray();
```

#### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta solución |
|---|---|---|
| `$unwind` | Emite una entrada por ejecución de `exp-006`. | Permite resolver cada referencia de modelo por separado. |
| `$lookup` | Busca en `modelos` el `_id` igual a cada `ejecuciones.modelo_id` y devuelve coincidencias en un array. | Recupera la versión actual que no forma parte del snapshot. |
| Segundo `$unwind` y `$project` | Simplifican el array encontrado y combinan campos históricos y actuales en la salida. | Muestran snapshot, identificador y versión vigente. |

**Resultado esperado:** el snapshot alcanza para mostrar el nombre registrado durante la ejecución; `$lookup` es necesario para datos actuales del catálogo, como su versión vigente.

### 5. Índice y medición

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.experimentos.createIndex(
  {"dataset.tipo_fuente": 1, fecha: -1},
  {name: "idx_tipo_fuente_fecha"},
);
practica.experimentos.find(
  {"dataset.tipo_fuente": "Sistema interno"},
).sort({fecha: -1}).explain("executionStats");
```

#### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta solución |
|---|---|---|
| `createIndex({"dataset.tipo_fuente": 1, fecha: -1}, ...)` | Crea un índice compuesto: fuente ascendente y fecha descendente. | Alinea primero el filtro por igualdad y luego el orden solicitado. |
| `.sort({fecha: -1})` | Solicita fechas de más reciente a más antigua. | Coincide con la segunda clave y dirección del índice. |
| `explain("executionStats")` | Ejecuta la consulta para devolver plan y estadísticas, no los documentos. | Permite comparar `winningPlan`, documentos examinados y resultados antes de afirmar una mejora. |

**Resultado esperado:** el índice queda disponible, pero con nueve documentos el optimizador puede elegir `COLLSCAN`. Compará `winningPlan`, `totalDocsExamined` y `nReturned`.

### 6. Modelo para métricas masivas

Separaría las muestras en una colección de series temporales. Para probar el modelo, creá la colección solo si todavía no existe:

```javascript
const practica = db.getSiblingDB("bdia_clase4");
if (!practica.getCollectionNames().includes("metricas_temporales")) {
  practica.createCollection("metricas_temporales", {
    timeseries: {
      timeField: "fecha",
      metaField: "meta",
      granularity: "seconds",
    },
  });
}
practica.metricas_temporales.createIndex(
  {"meta.experimento_id": 1, fecha: 1},
  {name: "idx_experimento_fecha"},
);
```

#### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta propuesta |
|---|---|---|
| `createCollection(nombre, opciones)` | Crea explícitamente una colección y devuelve un documento de respuesta. | Permite configurar `metricas_temporales` como colección de series temporales desde su creación. |
| `timeseries` | Agrupa las opciones específicas de una colección temporal, cuyos documentos MongoDB organiza internamente en buckets. | Prepara una colección adecuada para muchas mediciones fechadas. |
| `timeField` / `metaField` | Indican el campo de fecha obligatorio y el campo estable de metadatos usado para agrupar series. | Usan `fecha` como tiempo y `meta` para identificar experimento y métrica. |
| `granularity: "seconds"` | Informa la escala temporal esperada entre mediciones para orientar la organización interna. | Modela muestras que pueden llegar con precisión de segundos. |
| `createIndex` compuesto | Crea un índice por experimento y fecha sobre la colección temporal. | Favorece búsquedas de una serie dentro de un intervalo. |

Cargá muestras de prueba. La comprobación evita duplicarlas si volvés a ejecutar el bloque:

```javascript
const practica = db.getSiblingDB("bdia_clase4");
if (practica.metricas_temporales.countDocuments({"meta.experimento_id": "exp-006"}) === 0) {
  practica.metricas_temporales.insertMany([
    {
      fecha: ISODate("2026-06-15T10:30:00Z"),
      meta: {experimento_id: "exp-006", nombre: "accuracy"},
      valor: 0.94,
    },
    {
      fecha: ISODate("2026-06-15T10:31:00Z"),
      meta: {experimento_id: "exp-006", nombre: "loss"},
      valor: 0.18,
    },
    {
      fecha: ISODate("2026-06-16T10:30:00Z"),
      meta: {experimento_id: "exp-006", nombre: "accuracy"},
      valor: 0.95,
    },
  ]);
}
```

#### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta propuesta |
|---|---|---|
| `ISODate("...")` | Ayudante del shell que construye un valor BSON de tipo fecha a partir de una fecha ISO 8601. | Guarda `fecha` como valor temporal consultable, no como string. |
| `meta: {...}` | Subdocumento con valores que describen la serie y cambian con poca frecuencia. | Asocia la muestra con un experimento y un nombre de métrica. |
| `countDocuments(...) === 0` | Comprueba si ya existen muestras del experimento antes de insertar. | Permite repetir el bloque sin duplicar los datos de prueba. |
| `insertMany` | Inserta varias muestras en una sola operación. | Carga dos valores dentro del rango consultado y uno fuera para comprobar los límites. |
| `valor` | Campo numérico con la medición de cada muestra. | Almacena el valor observado en ese instante. |

La consulta por experimento y rango temporal sería:

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.metricas_temporales.find(
  {
    "meta.experimento_id": "exp-006",
    fecha: {
      $gte: ISODate("2026-06-15T00:00:00Z"),
      $lt: ISODate("2026-06-16T00:00:00Z"),
    },
  },
  {_id: 0, fecha: 1, "meta.nombre": 1, valor: 1},
).sort({fecha: 1}).toArray();
```

#### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta propuesta |
|---|---|---|
| `$gte` / `$lt` | Comparan “mayor o igual que” y “menor que”. Juntos forman un intervalo semiabierto: incluye el inicio y excluye el final. | Seleccionan las muestras del día indicado sin solapar el inicio del día siguiente. |
| Rango sobre `fecha` | Varias comparaciones dentro del mismo objeto se aplican al mismo campo. | Acota la serie temporal entre dos instantes. |
| Proyección y `sort` | La proyección limita la salida y el orden ascendente presenta primero la muestra más antigua. | Devuelve solo fecha, nombre y valor en orden cronológico. |

**Resultado esperado:** dos métricas del 15 de junio (`accuracy` y `loss`), ordenadas cronológicamente. La muestra del 16 de junio queda fuera porque el límite superior usa `$lt`. Separarlas evita superar el límite de 16 MB y concentra las escrituras en documentos administrados por buckets, en lugar de reescribir continuamente el experimento. El costo es resolver la referencia cuando se consultan el experimento y su serie juntos.

</details>
