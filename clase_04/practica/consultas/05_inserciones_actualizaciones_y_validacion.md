# 05. Inserciones, actualizaciones y validación

Abrí el **shell integrado de MongoDB Compass** y ejecutá los bloques **en el orden indicado**. Todos seleccionan `bdia_clase4`. Esta actividad modifica un documento temporal y lo elimina al final.

## 1. Crear un documento temporal

**Objetivo:** practicar la creación segura con `insertOne` sin alterar los datos base.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.experimentos.deleteOne({_id: "exp-temporal-clase"});
const base = practica.experimentos.findOne({_id: "exp-001"});
practica.experimentos.insertOne({
  ...base,
  _id: "exp-temporal-clase",
  nombre: "Experimento temporal de clase",
  etiquetas: ["temporal"],
});
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| `deleteOne(filtro)` | Método de colección que elimina como máximo un documento coincidente. Devuelve un **resultado de escritura** con campos como `acknowledged` y `deletedCount`. | Limpia una copia temporal que pudiera haber quedado de una ejecución previa. |
| `findOne` | Devuelve el documento encontrado o `null`. | Obtiene una plantilla que ya cumple la estructura esperada. |
| `insertOne(documento)` | Método de colección que inserta un documento y devuelve un **resultado de escritura** con `acknowledged` e `insertedId`; no devuelve el documento insertado. | Crea el experimento temporal. |
| `...base` | Sintaxis spread de JavaScript que copia las propiedades enumerables de `base` al nuevo objeto. Las propiedades escritas después reemplazan las del mismo nombre. | Reutiliza la estructura válida y luego cambia `_id`, `nombre` y `etiquetas`. |
| Arrays `[...]` | Representan listas ordenadas dentro del documento BSON. | Inicializan `etiquetas` con un único elemento. |

**Qué hace:** elimina un resto de una ejecución anterior, toma un documento válido como plantilla e inserta una copia con otro `_id`.

**Observá:** `acknowledged` debe ser `true` e `insertedId` debe valer `exp-temporal-clase`.

**Comparación con SQL:** `insertOne` es análogo a `INSERT`, pero inserta el documento completo con subdocumentos y arrays.

## 2. Leerlo con `findOne`

**Objetivo:** confirmar el estado creado.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.experimentos.findOne(
  {_id: "exp-temporal-clase"},
  {_id: 1, nombre: 1, finalizado: 1, etiquetas: 1},
);
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| `findOne(filtro, proyección)` | Busca un único documento y aplica la proyección del segundo argumento. Retorna un documento proyectado o `null`. | Verifica el temporal mostrando solo sus campos de control. |
| Proyección inclusiva | Los campos en `1` se incluyen; los demás se omiten, salvo `_id` si no se lo excluye. | Mantiene la comprobación breve. |

**Qué hace:** busca por `_id` y proyecta solo campos de control.

**Observá:** debe existir un único documento con la etiqueta `temporal`.

## 3. Actualizar campos y arrays

**Objetivo:** modificar un valor, evitar etiquetas duplicadas y agregar una nota embebida.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.experimentos.updateOne(
  {_id: "exp-temporal-clase"},
  {
    $set: {finalizado: true},
    $addToSet: {etiquetas: "revisado-en-clase"},
    $push: {notas: {autor: "estudiante", texto: "CRUD verificado"}},
  },
);
practica.experimentos.findOne(
  {_id: "exp-temporal-clase"},
  {_id: 1, finalizado: 1, etiquetas: 1, notas: 1},
);
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| `updateOne(filtro, actualización)` | Método de colección que actualiza como máximo el primer documento coincidente. Devuelve un **resultado de escritura** con `matchedCount` y `modifiedCount`. | Modifica exclusivamente el experimento temporal. |
| `$set` | Operador de actualización que crea o reemplaza el valor de campos sin sustituir el documento completo. | Cambia `finalizado` a `true`. |
| `$addToSet` | Agrega un valor a un array solo si todavía no existe un valor igual. | Evita duplicar la etiqueta al repetir el bloque. |
| `$push` | Agrega un valor al final de un array; no comprueba duplicados. Si el campo no existe, crea el array. | Añade el subdocumento de nota. |
| `{autor: ..., texto: ...}` | Es un subdocumento embebido usado como elemento del array. | Mantiene relacionados autor y texto dentro de `notas`. |

**Qué hace:** `$set` reemplaza un campo, `$addToSet` agrega solo si no existe y `$push` añade un elemento al array.

**Observá:** `modifiedCount` debe ser `1`; el documento queda finalizado y contiene la nueva nota.

## 4. Quitar un elemento del array

**Objetivo:** practicar `$pull` sin eliminar el documento.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.experimentos.updateOne(
  {_id: "exp-temporal-clase"},
  {$pull: {notas: {autor: "estudiante"}}},
);
practica.experimentos.findOne({_id: "exp-temporal-clase"}, {_id: 1, notas: 1});
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| `$pull` | Operador de actualización que elimina de un array todos los elementos que cumplen la condición dada. | Quita las notas cuyo `autor` es `estudiante` sin borrar el experimento. |
| Resultado de `updateOne` | Informa coincidencias y cambios; no contiene el documento actualizado. | La lectura posterior con `findOne` comprueba el estado resultante. |

**Qué hace:** elimina del array los elementos que cumplen el filtro.

**Observá:** la nota agregada deja de aparecer; el experimento permanece.

## 5. Configurar el validador

**Objetivo:** exigir una estructura mínima en inserciones y actualizaciones.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.runCommand({
  collMod: "experimentos",
  validator: {$jsonSchema: {
    bsonType: "object",
    required: ["_id", "nombre", "fecha", "finalizado", "dataset", "ejecuciones", "metricas"],
    properties: {
      _id: {bsonType: "string"},
      nombre: {bsonType: "string", minLength: 1},
      fecha: {bsonType: "date"},
      finalizado: {bsonType: "bool"},
      dataset: {bsonType: "object", required: ["dataset_id", "nombre", "propietario"]},
      ejecuciones: {bsonType: "array", minItems: 1},
      metricas: {bsonType: "object"},
    },
  }},
  validationLevel: "strict",
  validationAction: "error",
});
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| `runCommand({...})` | Ejecuta un comando de base de datos y devuelve un documento de respuesta, por ejemplo con `ok: 1`; no es un método CRUD de colección. | Envía la configuración del validador desde el shell de Compass. |
| `collMod: "experimentos"` | Comando administrativo que modifica opciones de una colección existente. | Asocia el nuevo validador a `experimentos`. |
| `validator` / `$jsonSchema` | Define reglas declarativas sobre la estructura y los valores aceptados. `$jsonSchema` usa palabras clave adaptadas a tipos BSON. | Exige la forma mínima del experimento en futuras escrituras. |
| `bsonType` | Restringe el tipo BSON del valor, como `object`, `string`, `date`, `bool` o `array`. No convierte datos. | Comprueba los tipos de documento y campos principales. |
| `required` | Enumera campos que deben existir en el objeto al que pertenece la regla. | Exige campos raíz y, dentro de `dataset`, sus campos esenciales. |
| `properties` | Asocia reglas específicas con campos del objeto. | Define validaciones distintas para cada campo conocido. |
| `minLength: 1` / `minItems: 1` | Exigen al menos un carácter en un string o un elemento en un array. | Evitan nombres vacíos y experimentos sin ejecuciones. |
| `validationLevel: "strict"` | Aplica la validación a todas las inserciones y a las actualizaciones afectadas. | Mantiene la regla activa de forma estricta. |
| `validationAction: "error"` | Rechaza la escritura inválida en lugar de permitirla con una advertencia. | Hace observable el error del siguiente ejercicio. |

**Qué hace:** aplica `$jsonSchema` a la colección desde el shell de Compass.

**Observá:** el comando debe responder `ok: 1`. En Compass también podés inspeccionarlo desde la pestaña **Validation** de la colección.

**Comparación con SQL:** se parece a restricciones de esquema, pero se define sobre la forma del documento y sus tipos BSON.

## 6. Error esperado por validación

**Objetivo:** comprobar que el validador rechaza documentos incompletos.

Ejecutá este bloque solo. **Debe fallar** con código `121` o `DocumentValidationFailure`; el error visible es el resultado esperado.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.experimentos.insertOne({_id: "exp-invalido-clase", nombre: "Sin estructura"});
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| `insertOne` con documento incompleto | Intenta una escritura normal, por lo que se evalúa el validador activo. | Provoca deliberadamente `DocumentValidationFailure` porque faltan campos requeridos. |
| Error de escritura | La operación lanza un error y no produce un resultado de inserción exitoso. El código `121` identifica el fallo de validación. | Confirma que el documento inválido no se almacenó. |

**Qué hace:** intenta insertar un documento sin los campos obligatorios.

**Observá:** no debe insertarse `exp-invalido-clase`. No se usa `catch`: cualquier error distinto también queda visible para investigarlo.

## 7. Error esperado por `_id` duplicado

**Objetivo:** comprobar la unicidad automática de `_id`.

Ejecutá este bloque solo. **Debe fallar** con código `11000` o `DuplicateKey`.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
const existente = practica.experimentos.findOne({_id: "exp-001"});
practica.experimentos.insertOne(existente);
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| `insertOne(existente)` | Intenta insertar otra vez el documento completo, incluido su `_id`. | Activa la restricción única del índice automático de `_id`. |
| Error `11000` / `DuplicateKey` | Indica que una escritura intentó repetir una clave única; la operación se rechaza. | Demuestra que no pueden coexistir dos documentos con `_id: "exp-001"`. |

**Qué hace:** intenta insertar nuevamente un documento con el mismo `_id`.

**Observá:** la colección mantiene una sola copia de `exp-001`.

**Comparación con SQL:** `_id` funciona como clave primaria única y siempre tiene un índice asociado.

## 8. Eliminar y verificar la limpieza

**Objetivo:** completar CRUD con `deleteOne` y restaurar el estado de documentos.

```javascript
const practica = db.getSiblingDB("bdia_clase4");
practica.experimentos.deleteOne({_id: "exp-temporal-clase"});
practica.experimentos.findOne({_id: "exp-temporal-clase"});
practica.experimentos.countDocuments();
```

### Comandos y operadores

| Elemento/sintaxis | Qué hace | Para qué se utiliza en esta consulta |
|---|---|---|
| `deleteOne` | Elimina como máximo una coincidencia y retorna un resultado de escritura con `deletedCount`. | Borra únicamente el documento temporal. |
| `findOne` y `null` | Cuando no existe una coincidencia, `findOne` devuelve `null`. | Verifica directamente que el temporal ya no está. |
| `countDocuments()` | Cuenta los documentos que cumplen un filtro; sin argumento cuenta todos los de la colección. Devuelve un número, no un cursor. | Confirma que la colección regresó a nueve documentos. |

**Qué hace:** elimina solo el documento temporal y comprueba su ausencia.

**Observá:** `deletedCount` debe ser `1`, `findOne` devuelve `null` y la colección vuelve a tener `9` documentos. El validador queda activo; para restaurar toda la colección, volvé a ejecutar `00_cargar_datos.js` con el comando Docker del README.
