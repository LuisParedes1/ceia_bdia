# 03. Consultas básicas

Abrí el **shell integrado de MongoDB Compass** y ejecutá cada bloque por separado. Todos trabajan sobre `bdia_clase4`.

## Filtrar y ordenar

**Objetivo:** listar experimentos pendientes en orden cronológico.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.experimentos.find(
  {finalizado: false},
  {_id: 1, nombre: 1, fecha: 1},
).sort({fecha: 1}).toArray();
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| `{finalizado: false}` | Filtro por igualdad implícita; equivale a expresar que el campo debe ser exactamente booleano `false`. | Conserva solo experimentos pendientes. |
| Segundo argumento de `find` | Es la proyección, separada del filtro del primer argumento. Los valores `1` incluyen los campos indicados. | Limita cada documento a `_id`, `nombre` y `fecha`. |
| `.sort({fecha: 1})` | Ordena el cursor por fecha ascendente antes de materializarlo. | Presenta los pendientes en orden cronológico. |
| Resultado | `find` devuelve un cursor y `toArray()` lo convierte en un array de documentos proyectados. | Permite ver juntos todos los pendientes. |

**Qué hace:** combina filtro, proyección y orden.

**Observá:** solo aparecen documentos con `finalizado: false`, sin campos no proyectados.

**Comparación con SQL:** corresponde a `WHERE`, selección de columnas y `ORDER BY`.

## Consultar un subdocumento

**Objetivo:** filtrar por tipo de fuente y devolver solo datos del dataset.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.experimentos.find(
  {"dataset.tipo_fuente": "Sistema interno"},
  {_id: 0, nombre: 1, "dataset.nombre": 1, "dataset.cantidad_registros": 1},
).toArray();
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| Rutas `dataset.*` | La notación de punto consulta y proyecta campos de un subdocumento. En la salida proyectada se conserva la estructura anidada. | Filtra por `tipo_fuente` y muestra solo nombre y cantidad de registros del dataset. |
| `_id: 0` | Excluye `_id`, excepción permitida al usar una proyección inclusiva con campos en `1`. | Evita un identificador que no aporta al objetivo del bloque. |

**Qué hace:** navega campos embebidos con notación de puntos.

**Observá:** cada resultado conserva la estructura anidada de `dataset`.

## Proyectar un elemento del array

**Objetivo:** encontrar y mostrar la ejecución con configuración balanceada.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.experimentos.find(
  {"ejecuciones.parametros.class_weight": "balanced"},
  {_id: 1, nombre: 1, ejecuciones: {$elemMatch: {"parametros.class_weight": "balanced"}}},
).toArray();
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| Ruta a través de `ejecuciones` | El filtro coincide cuando al menos un elemento del array contiene el parámetro buscado. | Selecciona experimentos con alguna configuración balanceada. |
| `$elemMatch` en proyección | Conserva el primer elemento del array que satisface el criterio indicado. | Evita devolver ejecuciones no relacionadas con `class_weight: "balanced"`. |

**Qué hace:** filtra por un valor interno y proyecta únicamente el primer elemento coincidente.

**Observá:** el array `ejecuciones` de cada salida contiene solo la ejecución relevante.

**Comparación con SQL:** se relaciona con consultar JSONB, pero `$elemMatch` expresa que se trabaja sobre elementos de un array BSON.

## Existencia y rango

**Objetivo:** distinguir métricas heterogéneas y aplicar una condición numérica.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.experimentos.find(
  {"metricas.mae": {$exists: true}},
  {_id: 0, nombre: 1, "metricas.mae": 1},
).toArray();

practica.experimentos.find(
  {"metricas.accuracy": {$gte: 0.85}},
  {_id: 0, nombre: 1, "metricas.accuracy": 1},
).sort({"metricas.accuracy": -1}).toArray();
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| `$exists: true` | Operador de consulta que exige que la ruta exista, independientemente de cuál sea su valor. | Distingue experimentos que registran la métrica `mae`. |
| `$gte: 0.85` | Operador de comparación “mayor o igual que”. | Selecciona valores de `accuracy` desde `0.85`, inclusive. |
| `.sort({"metricas.accuracy": -1})` | Ordena el cursor por una ruta anidada; `-1` indica orden descendente. | Muestra primero el accuracy más alto. |

**Qué hace:** la primera consulta exige que exista `mae`; la segunda filtra `accuracy` por rango.

**Observá:** regresión y clasificación pueden almacenar métricas distintas sin columnas nulas compartidas.
