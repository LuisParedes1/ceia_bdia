# 01. Revisar el origen relacional

Abrí el **shell integrado de MongoDB Compass**, seleccioná la conexión local y ejecutá cada bloque por separado. Todos los bloques eligen explícitamente `bdia_clase4`.

## Colecciones de origen

**Objetivo:** reconocer las ocho tablas de la clase anterior cargadas como colecciones de observación.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.getCollectionNames().filter((nombre) => nombre.startsWith("origen_")).sort();
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| `db.getSiblingDB("bdia_clase4")` | Obtiene una referencia a otra base de datos sin cambiar globalmente la base activa del shell. | Asegura que el resto del bloque trabaje sobre `bdia_clase4`. |
| `const practica = ...` | Guarda esa referencia en una constante de JavaScript. | Permite escribir `practica.<colección>` en las instrucciones siguientes. |
| `getCollectionNames()` | Devuelve un array de JavaScript con los nombres de las colecciones de la base. | Proporciona el inventario que luego se filtra y ordena. |
| `.filter((nombre) => ...)` | Conserva en un array solo los elementos para los que la función devuelve `true`. | Descarta los nombres que no comienzan con `origen_`. |
| `.startsWith("origen_")` | Comprueba si un texto comienza con el prefijo indicado. | Identifica las colecciones importadas desde el modelo relacional. |
| `.sort()` | Ordena el array de nombres alfabéticamente. Aquí es el método de arrays de JavaScript, no el ordenamiento de un cursor. | Hace estable y fácil de revisar la lista obtenida. |

**Qué hace:** lista únicamente las colecciones que conservan la estructura relacional.

**Observá:** deben aparecer ocho nombres `origen_*`. Cada documento todavía representa una fila.

## Datos distribuidos

**Objetivo:** reconstruir manualmente las partes del experimento relacional `6`.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.origen_experimentos.findOne({id: 6});
practica.origen_experimentos_modelos.find({experimento_id: 6}).sort({modelo_id: 1}).toArray();
practica.origen_metricas.find({experimento_id: 6}).sort({id: 1}).toArray();
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| `findOne(filtro)` | Método de colección que devuelve el primer documento que cumple el filtro, o `null` si no hay coincidencias. | Recupera el único experimento cuyo `id` es `6`. El resultado es un **documento**, no un cursor. |
| `find(filtro)` | Método de colección que prepara una consulta y devuelve un **cursor**, es decir, un objeto que permite recorrer, ordenar o transformar los resultados sin cargarlos todavía como array. | Busca todas las relaciones y métricas asociadas al experimento `6`. |
| `{experimento_id: 6}` | Es el filtro de `find`: cada par `campo: valor` exige igualdad implícita. | Selecciona documentos cuya clave de relación apunta al experimento `6`. |
| `.sort({modelo_id: 1})` / `.sort({id: 1})` | Ordena el cursor por el campo indicado; `1` significa ascendente y `-1`, descendente. | Presenta modelos y métricas en un orden reproducible. |
| `.toArray()` | Consume el cursor y materializa sus resultados como un array de documentos en el shell. | Muestra juntos todos los resultados en Compass. |

**Qué hace:** consulta la fila principal, sus modelos y sus métricas mediante claves.

**Observá:** el contexto queda repartido entre tres colecciones y todavía faltan dataset y usuario.

**Comparación con SQL:** equivale a consultar tablas normalizadas por clave foránea antes de combinarlas.

## Reconstrucción con `$lookup`

**Objetivo:** obtener experimento, dataset y propietario en una sola salida.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.origen_experimentos.aggregate([
  {$match: {id: 6}},
  {$lookup: {from: "origen_datasets", localField: "dataset_id", foreignField: "id", as: "dataset"}},
  {$unwind: "$dataset"},
  {$lookup: {from: "origen_usuarios", localField: "dataset.usuario_id", foreignField: "id", as: "usuario"}},
  {$unwind: "$usuario"},
  {$project: {_id: 0, experimento: "$nombre", dataset: "$dataset.nombre", usuario: "$usuario.nombre"}},
]).toArray();
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| `aggregate([...])` | Método de colección que ejecuta una pipeline: una secuencia de etapas donde cada salida alimenta a la siguiente. Devuelve un **cursor de agregación**. | Reconstruye y transforma información distribuida entre colecciones. |
| `$match` | Etapa que deja pasar solo los documentos que cumplen un filtro. | Inicia la pipeline con el experimento `6`, evitando combinar documentos innecesarios. |
| `$lookup` | Etapa que busca coincidencias en otra colección y agrega un array con los documentos encontrados. | Une el experimento con su dataset y luego con el usuario propietario. |
| `from` | Indica la colección externa consultada por `$lookup`. | Selecciona primero `origen_datasets` y después `origen_usuarios`. |
| `localField` / `foreignField` | Comparan el valor del campo local con el campo de la colección externa. | Relacionan `dataset_id` con `id` y `dataset.usuario_id` con `id`. |
| `as` | Nombra el nuevo campo array donde `$lookup` coloca las coincidencias. | Crea los campos temporales `dataset` y `usuario`. |
| `$unwind: "$campo"` | Etapa que emite un documento por cada elemento de un array. | Convierte los arrays de una coincidencia creados por `$lookup` en subdocumentos simples. |
| `$project` | Etapa que define la forma del resultado: puede incluir, excluir, renombrar o calcular campos. | Devuelve únicamente los nombres del experimento, dataset y usuario. |
| `_id: 0` | Exclusión explícita dentro de una proyección. | Evita que el identificador aparezca en la salida. |
| `experimento: "$nombre"` | En agregación, un texto que comienza con `$` referencia el valor de un campo; la clave de la izquierda asigna el nombre de salida. | Renombra `nombre` como `experimento`. |
| `.toArray()` | Materializa el cursor de agregación como array; no cambia los documentos almacenados. | Muestra la salida completa de la pipeline. |

**Qué hace:** enlaza dos colecciones y transforma los arrays resultantes en documentos simples.

**Observá:** devuelve una fila lógica con los tres nombres.

**Comparación con SQL:** `$lookup` cumple un papel comparable a `JOIN`; `$project` se parece a elegir columnas con `SELECT`.

## Campo variable heredado

**Objetivo:** filtrar un atributo dentro de los parámetros que antes estaban en JSONB.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.origen_experimentos_modelos.find(
  {"parametros_jsonb.class_weight": "balanced"},
  {_id: 0, experimento_id: 1, modelo_id: 1, parametros_jsonb: 1},
).toArray();
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| `find(filtro, proyección)` | El primer argumento selecciona documentos; el segundo controla qué campos devuelve cada resultado. Sigue retornando un cursor. | Filtra por `class_weight` y limita la salida a los identificadores y parámetros relevantes. |
| `"parametros_jsonb.class_weight"` | La notación de punto recorre campos de subdocumentos, sin tratar el objeto como texto. | Accede a `class_weight` dentro de `parametros_jsonb`. |
| `{_id: 0, ...: 1}` | En una proyección, `1` incluye campos y `_id: 0` excluye el identificador, que se incluye por defecto. | Construye una salida compacta sin `_id`. |

**Qué hace:** usa notación con puntos para entrar en un objeto.

**Observá:** aparecen solo las relaciones cuyo parámetro `class_weight` vale `balanced`.

**Comparación con SQL:** la intención es similar a consultar una clave JSONB, pero el objeto ya forma parte natural del documento BSON.
