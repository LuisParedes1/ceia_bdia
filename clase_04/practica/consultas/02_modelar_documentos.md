# 02. Modelar documentos

Abrí el **shell integrado de MongoDB Compass** y ejecutá cada bloque por separado. Los bloques seleccionan `bdia_clase4` explícitamente.

## Datos embebidos

**Objetivo:** inspeccionar un experimento diseñado para leerse como una unidad.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.experimentos.findOne({_id: "exp-006"});
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| `findOne({_id: "exp-006"})` | Recupera un documento por igualdad de `_id`; devuelve el documento o `null`, no un cursor. | Permite inspeccionar de una vez el agregado con sus subdocumentos y arrays embebidos. |
| `_id` | Campo identificador obligatorio y único de cada documento de una colección. Puede usar tipos distintos de `ObjectId`; aquí es un string. | Identifica de forma estable el experimento `exp-006`. |

**Qué hace:** recupera un documento con dataset, propietario, ejecuciones y métricas embebidos.

**Observá:** una lectura entrega el contexto que en el origen requería varias tablas.

**Comparación con SQL:** se reduce la necesidad de `JOIN`, a cambio de duplicar datos elegidos según el patrón de acceso.

## Modelo referenciado

**Objetivo:** comprobar cómo una ejecución combina snapshot embebido y referencia reutilizable.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.modelos.findOne({_id: "mod-006"});
practica.experimentos.find(
  {"ejecuciones.modelo_id": "mod-006"},
  {_id: 1, nombre: 1, ejecuciones: {$elemMatch: {modelo_id: "mod-006"}}},
).toArray();
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| `"ejecuciones.modelo_id"` | Una ruta con puntos puede atravesar un array de subdocumentos; el filtro coincide si algún elemento contiene ese valor. | Encuentra experimentos que referencian `mod-006`. |
| `$elemMatch` en proyección | Devuelve únicamente el primer elemento del array que cumple la condición. No reemplaza el filtro general de la consulta. | Reduce `ejecuciones` a la ejecución que usa `mod-006`. |
| `findOne` frente a `find` | `findOne` produce un documento o `null`; `find` produce un cursor potencialmente con varios documentos. | La primera lectura espera un modelo único y la segunda, todos los experimentos relacionados. |

**Qué hace:** busca el modelo actual y los experimentos que guardan su identificador.

**Observá:** `modelo_id` referencia el catálogo, mientras `modelo_nombre` y `tipo_modelo` conservan un snapshot útil para lectura.

## Proyección derivada

**Objetivo:** producir una vista de lectura sin crear otra colección.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.experimentos.aggregate([
  {$project: {_id: 0, experimento: "$nombre", dataset: "$dataset.nombre", usuario: "$dataset.propietario.nombre", finalizado: 1}},
  {$sort: {usuario: 1, dataset: 1, experimento: 1}},
]).toArray();
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| `$project` | Da forma a cada documento de salida; las rutas con `$` leen valores del documento de entrada y `1` conserva un campo con su nombre actual. | Renombra campos embebidos y conserva `finalizado`. |
| `$sort` | Etapa de agregación que ordena los documentos que recibe; aplica las claves de izquierda a derecha y `1` indica orden ascendente. | Ordena por usuario, luego dataset y finalmente experimento. |
| Resultado de `aggregate` | Es un cursor de agregación hasta llamar a `toArray()`. La proyección es una vista del resultado, no una escritura. | Produce nueve documentos de lectura sin crear ni modificar una colección. |

**Qué hace:** renombra y selecciona campos embebidos para una salida específica.

**Observá:** la pipeline devuelve nueve experimentos sin modificar los documentos.

**Comparación con SQL:** cumple una función de lectura similar a una vista o a un `SELECT` con alias, pero no es una entidad persistida.
