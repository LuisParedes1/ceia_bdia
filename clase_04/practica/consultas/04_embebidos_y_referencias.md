# 04. Embebidos y referencias

Abrí el **shell integrado de MongoDB Compass** y ejecutá cada bloque por separado sobre `bdia_clase4`.

## Condiciones sobre el mismo elemento

**Objetivo:** encontrar experimentos con una ejecución de clasificación cuyo umbral sea menor que `0.5`.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.experimentos.find(
  {ejecuciones: {$elemMatch: {tipo_modelo: "Clasificación", "parametros.threshold": {$lt: 0.5}}}},
  {_id: 1, nombre: 1, ejecuciones: 1},
).toArray();
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| `$elemMatch` en filtro | Exige que un mismo elemento del array cumpla todas las condiciones incluidas. | Garantiza que `tipo_modelo` y `threshold` pertenezcan a una única ejecución, en lugar de combinar coincidencias de elementos distintos. |
| `$lt: 0.5` | Operador de comparación “menor que”; el límite no está incluido. | Restringe el umbral de esa ejecución a valores inferiores a `0.5`. |
| `"parametros.threshold"` | Ruta con puntos relativa al elemento evaluado por `$elemMatch`. | Accede al umbral dentro de los parámetros de cada ejecución. |

**Qué hace:** `$elemMatch` obliga a que ambas condiciones correspondan a la misma ejecución.

**Observá:** no se mezclan valores pertenecientes a dos elementos diferentes del array.

## Desarmar un array para analizarlo

**Objetivo:** obtener una fila lógica por ejecución.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.experimentos.aggregate([
  {$unwind: "$ejecuciones"},
  {$project: {_id: 0, experimento: "$nombre", modelo_id: "$ejecuciones.modelo_id", parametros: "$ejecuciones.parametros"}},
  {$sort: {experimento: 1, modelo_id: 1}},
]).toArray();
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| `$unwind: "$ejecuciones"` | Emite una salida por elemento del array y reemplaza temporalmente `ejecuciones` por el elemento actual. | Permite tratar cada ejecución como una fila lógica durante la pipeline. |
| `$project` | Selecciona y renombra campos de cada salida generada por `$unwind`. | Muestra experimento, modelo y parámetros sin `_id`. |
| `$sort` | Ordena el cursor de agregación por las claves indicadas. | Agrupa visualmente las ejecuciones por experimento y modelo. |

**Qué hace:** `$unwind` genera una salida por elemento sin cambiar los documentos almacenados.

**Observá:** hay más resultados que experimentos porque alguno posee varias ejecuciones.

**Comparación con SQL:** la salida tabular se parece a expandir una relación uno-a-muchos, aunque el array sigue embebido.

## Resolver una referencia

**Objetivo:** consultar la versión y el propietario actuales de los modelos usados por `exp-006`.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.experimentos.aggregate([
  {$match: {_id: "exp-006"}},
  {$unwind: "$ejecuciones"},
  {$lookup: {from: "modelos", localField: "ejecuciones.modelo_id", foreignField: "_id", as: "modelo_actual"}},
  {$unwind: "$modelo_actual"},
  {$project: {_id: 0, experimento: "$nombre", snapshot: "$ejecuciones.modelo_nombre", version_actual: "$modelo_actual.version", propietario: "$modelo_actual.propietario.nombre"}},
]).toArray();
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| `$match` | Reduce la entrada de la pipeline al experimento indicado. | Resuelve referencias únicamente para `exp-006`. |
| `$unwind` antes de `$lookup` | Genera una entrada separada por ejecución. | Hace que cada `modelo_id` se combine de manera individual. |
| `$lookup` | Compara `ejecuciones.modelo_id` con `_id` en `modelos` y guarda coincidencias en el array `modelo_actual`. | Recupera información vigente del catálogo referenciado. |
| Segundo `$unwind` | Convierte el array `modelo_actual` en un subdocumento. | Habilita rutas directas como `$modelo_actual.version` en la proyección. |
| Resultado | `aggregate` devuelve un cursor de agregación y `toArray()` lo materializa; no crea integridad referencial ni modifica datos. | Presenta juntos snapshot histórico y datos actuales. |

**Qué hace:** usa el identificador guardado en cada ejecución para recuperar el modelo vigente.

**Observá:** el snapshot sirve para mostrar el nombre histórico; `$lookup` se justifica al necesitar datos actuales no embebidos.

**Comparación con SQL:** la referencia y `$lookup` son comparables a clave foránea y `JOIN`, pero MongoDB no impone esa integridad automáticamente.
