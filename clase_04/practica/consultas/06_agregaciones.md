# 06. Agregaciones

Abrí el **shell integrado de MongoDB Compass** y ejecutá cada pipeline por separado sobre `bdia_clase4`. También podés pegar solo el array de etapas en la pestaña **Aggregations** y ejecutar desde allí.

## Promedio por tipo de fuente

**Objetivo:** resumir cantidad y accuracy promedio por origen de datos.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.experimentos.aggregate([
  {$match: {"metricas.accuracy": {$exists: true}}},
  {$group: {_id: "$dataset.tipo_fuente", experimentos: {$sum: 1}, accuracy_promedio: {$avg: "$metricas.accuracy"}}},
  {$sort: {accuracy_promedio: -1}},
]).toArray();
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| `$match` + `$exists` | Filtra la entrada a documentos donde existe `metricas.accuracy`. | Evita agrupar experimentos que no poseen esa métrica. |
| `$group` | Reúne documentos por la expresión de `_id` y produce un documento de resultado por grupo. Los demás campos deben calcularse con acumuladores. | Crea un grupo por cada `dataset.tipo_fuente`. |
| `_id: "$dataset.tipo_fuente"` | Define la clave de agrupación a partir del valor de esa ruta. | Identifica cada tipo de fuente en el resultado. |
| `$sum: 1` | Acumulador que suma `1` por cada documento del grupo. | Calcula cuántos experimentos medidos hay por fuente. |
| `$avg: "$metricas.accuracy"` | Acumulador que obtiene el promedio de los valores numéricos recibidos. | Calcula `accuracy_promedio` por fuente. |
| `$sort: {accuracy_promedio: -1}` | Ordena los grupos ya calculados de mayor a menor promedio. | Presenta primero la fuente con mayor accuracy promedio. |
| Resultado agrupado | Es un documento nuevo de la pipeline por grupo, materializado desde el cursor con `toArray()`; no es un experimento almacenado. | Expone el resumen solicitado sin persistirlo. |

**Qué hace:** filtra experimentos medidos, agrupa por tipo de fuente y calcula dos acumuladores.

**Observá:** cada resultado representa un tipo de fuente, no un documento original.

**Comparación con SQL:** `$group` y `$avg` son comparables a `GROUP BY` y `AVG`.

## Ranking por tipo de modelo

**Objetivo:** ordenar ejecuciones por accuracy dentro de cada tipo de modelo.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.experimentos.aggregate([
  {$match: {"metricas.accuracy": {$exists: true}}},
  {$unwind: "$ejecuciones"},
  {$setWindowFields: {
    partitionBy: "$ejecuciones.tipo_modelo",
    sortBy: {"metricas.accuracy": -1},
    output: {posicion: {$rank: {}}},
  }},
  {$project: {_id: 0, tipo_modelo: "$ejecuciones.tipo_modelo", modelo: "$ejecuciones.modelo_nombre", experimento: "$nombre", accuracy: "$metricas.accuracy", posicion: 1}},
  {$sort: {tipo_modelo: 1, posicion: 1}},
]).toArray();
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| `$unwind` | Genera una entrada por ejecución antes del cálculo de ventana. | Permite asignar posición a cada modelo ejecutado. |
| `$setWindowFields` | Etapa que calcula valores sobre ventanas de documentos sin reducirlos a un documento por grupo. | Añade un ranking conservando cada ejecución en la salida. |
| `partitionBy` | Divide la entrada en particiones independientes. | Reinicia el ranking para cada `tipo_modelo`. |
| `sortBy` | Define el orden interno usado por los cálculos de ventana. | Ordena cada partición por accuracy descendente. |
| `output` | Nombra los campos calculados por la etapa. | Crea el campo `posicion`. |
| `$rank: {}` | Operador de ventana que asigna rango según `sortBy`; los empates comparten posición y pueden dejar saltos posteriores. | Produce el ranking solicitado dentro de cada tipo. |

**Qué hace:** expande ejecuciones y aplica una ventana con ranking por partición.

**Observá:** `posicion` reinicia al cambiar `tipo_modelo`; empates comparten rango.

**Comparación con SQL:** `$setWindowFields` cumple una función comparable a `RANK() OVER (PARTITION BY ...)`.

## Diferencia entre métricas

**Objetivo:** comparar precision y recall solo donde ambas existen.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.experimentos.aggregate([
  {$match: {"metricas.precision": {$exists: true}, "metricas.recall": {$exists: true}}},
  {$project: {_id: 0, nombre: 1, precision: "$metricas.precision", recall: "$metricas.recall", diferencia: {$subtract: ["$metricas.precision", "$metricas.recall"]}}},
  {$sort: {diferencia: -1}},
]).toArray();
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| Varias condiciones en `$match` | Las condiciones de campos diferentes dentro del mismo objeto se combinan con un AND implícito. | Exige que existan tanto `precision` como `recall`. |
| `$subtract: [valor1, valor2]` | Operador de expresión que resta el segundo valor al primero. | Calcula `precision - recall` para cada documento. |
| Campo derivado en `$project` | Existe solo en los documentos emitidos por la pipeline. | Permite ordenar por `diferencia` sin escribirla en la colección. |

**Qué hace:** calcula un campo derivado durante la pipeline.

**Observá:** `diferencia` no se persiste; existe únicamente en el resultado.
