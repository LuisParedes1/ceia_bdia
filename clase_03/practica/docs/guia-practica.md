# Guía práctica Clase 3

Esta guía acompaña los scripts SQL de la Clase 3.

## Punto de partida

La práctica parte de la base creada en `clase_02/practica`.

Antes de comenzar, la base debe tener creadas y cargadas estas tablas:

- `usuarios`
- `datasets`
- `modelos`
- `experimentos`
- `experimentos_modelos`
- `metricas`

No hace falta crear otro entorno Docker.
Reutilizá los contenedores PostgreSQL y pgAdmin desde `clase_02/practica`.

```bash
cd clase_02/practica
docker compose up -d
```

Antes de empezar con las consultas, ejecutá
`sql/00_poblar_datos_clase_03.sql`. Ese script agrega más datos de práctica
sin borrar ni reemplazar los datos de Clase 2.

## Objetivo general

Avanzar desde consultas simples sobre una tabla hacia consultas analíticas que
combinen varias tablas, calculen indicadores, comparen resultados y preparen
la base para usos más flexibles.

## Caso guía

El caso representa una plataforma simple para gestionar experimentos de IA:

- Los usuarios cargan datasets.
- Los usuarios registran modelos.
- Los datasets se usan en experimentos.
- Los experimentos pueden evaluar uno o más modelos.
- Los experimentos generan métricas.

Relaciones principales:

```text
usuarios 1:N datasets
usuarios 1:N modelos
datasets 1:N experimentos
experimentos N:M modelos
experimentos 1:N metricas
```

## 0. Poblar más datos

Script: `sql/00_poblar_datos_clase_03.sql`

La Clase 2 deja una base chica, suficiente para aprender `CREATE TABLE`,
`INSERT`, `SELECT` y restricciones. Para Clase 3 conviene tener más casos:
varios usuarios, más datasets, más experimentos por dataset, distintos modelos
y más métricas comparables.

Este script amplía la base sin romper lo anterior. Mantiene un estilo simple,
parecido al script de inserción de Clase 2. Está pensado para ejecutarse una
sola vez sobre una base limpia ya cargada con los datos de Clase 2.

### Qué observar al poblar datos

- Aparecen más filas en todas las tablas principales.
- Queda al menos un usuario sin datasets.
- Queda al menos un dataset sin experimentos.
- Hay más métricas `accuracy`, `precision`, `recall` y `f1_score` para comparar.

### Preguntas sobre datos de práctica

- ¿Por qué las agregaciones tienen más sentido con más filas?
- ¿Por qué conviene ejecutar los scripts de carga en el orden indicado?
- ¿Qué casos especiales ayudan a probar `LEFT JOIN`?

## 1. Ejercicio de normalización

Script: `sql/01_normalizacion.sql`

Clase 2 creó `datasets.fuente` y `modelos.tipo` como texto libre. Ambas
columnas repiten valores de categoría en varias filas: por ejemplo,
varios modelos comparten el valor `'Clasificación'` en `tipo`. Ese es el
problema típico que motiva normalizar: la categoría no tiene entidad
propia, así que no se puede corregir ni describir en un solo lugar, y
nada impide que dos filas escriban la misma categoría de formas
distintas.

Este ejercicio aplica 1FN/2FN/3FN al caso real de la base:

- Crea `tipos_fuente` y `tipos_modelo` como tablas catálogo.
- Agrega `datasets.tipo_fuente_id` y `modelos.tipo_modelo_id` como
  claves foráneas, completadas a partir del texto que ya existía.
- Conserva el detalle específico de cada dataset en
  `datasets.fuente_detalle`.
- Elimina las columnas de texto libre originales (`fuente` y `tipo`).

### Qué observar en la normalización

- `tipos_modelo` sale directo de los valores repetidos en `modelos.tipo`:
  cada categoría queda en una sola fila, sin importar cuántos modelos la
  usen.
- `tipos_fuente` agrupa textos distintos (`'IoT'`, `'IoT industrial'`)
  bajo una misma categoría. Agrupar así es una decisión de diseño, no un
  resultado automático.
- Después de este script, todos los scripts siguientes consultan
  `tipos_fuente` y `tipos_modelo` en lugar de las columnas de texto
  libre originales.

### Preguntas sobre normalización

- ¿Qué problema concreto evita mover `tipo` a una tabla catálogo?
- ¿Por qué `fuente_detalle` no se elimina junto con `fuente`?
- ¿Qué otra columna de la base te parece candidata a normalizar?

## 2. Revisar el esquema

Script: `sql/02_revisar_esquema.sql`

Primero miramos qué datos existen y qué columnas tiene cada tabla. También
revisamos restricciones para recordar cómo PostgreSQL protege la consistencia
de los datos.

### Qué observar en el esquema

- Qué columna identifica a cada tabla.
- Qué columnas conectan tablas entre sí.
- Qué tipos de datos se eligieron para cada atributo.
- Qué restricciones existen: claves primarias, claves foráneas, `UNIQUE` y
  `CHECK`.

### Preguntas sobre el esquema

- ¿Qué tabla representa la entidad central del caso?
- ¿Qué columnas funcionan como puentes entre tablas?
- ¿Qué errores evita una clave foránea?

## 3. Consultas con JOIN

Script: `sql/03_consultas_joins.sql`

Un `JOIN` permite combinar filas de distintas tablas cuando existe una relación
entre ellas. En este caso, nos permite pasar de usuarios a datasets, de
datasets a experimentos y de experimentos a métricas.

### Qué observar en los JOINs

- Un solo `JOIN` alcanza cuando las tablas están directamente conectadas.
- Para llegar desde usuarios hasta métricas se necesitan varios `JOIN`.
- `LEFT JOIN` permite detectar datos faltantes, por ejemplo datasets sin
  experimentos.

### Preguntas sobre JOINs

- ¿Qué tabla conecta usuarios con datasets?
- ¿Por qué necesitamos más de un `JOIN` para llegar desde usuarios hasta
  métricas?

## 4. Agregaciones y rankings

Script: `sql/04_agregaciones_rankings.sql`

Las agregaciones resumen datos: cuentan, promedian, calculan mínimos y máximos.
Son fundamentales para pasar de registros individuales a indicadores.

### Qué observar en las agregaciones

- `GROUP BY` define el nivel de agrupación.
- `WHERE` filtra filas antes de agrupar.
- `HAVING` filtra grupos después de agrupar.
- Los promedios por modelo permiten comparar desempeño entre alternativas.

### Preguntas sobre agregaciones

- ¿Qué diferencia hay entre `WHERE` y `HAVING`?
- ¿Qué indicador permite comparar datasets?

## 5. Subconsultas y funciones de ventana

Script: `sql/05_subconsultas_ventanas.sql`

Las subconsultas permiten comparar un valor contra otro conjunto de datos. Las
funciones de ventana permiten calcular valores agregados sin perder el detalle
de cada fila.

### Qué observar en ventanas

- Una subconsulta puede devolver un valor usado por la consulta principal.
- `ROW_NUMBER` permite ordenar y numerar filas dentro de un grupo.
- `AVG(...) OVER (...)` muestra el promedio del grupo al lado de cada fila
  original.

### Preguntas sobre ventanas

- ¿Qué diferencia hay entre `GROUP BY` y una función de ventana?
- ¿Por qué `ROW_NUMBER` permite rankear sin perder filas?

## 6. EXPLAIN, índices y medición

Script: `sql/06_explain_indices.sql`

Antes de optimizar hay que medir. `EXPLAIN ANALYZE` muestra el plan elegido por
PostgreSQL y el tiempo real de ejecución.

### Qué observar en índices

- En tablas pequeñas, PostgreSQL puede preferir `Seq Scan` aunque exista un
  índice.
- Un índice no es magia: mejora algunos accesos y agrega costo en escrituras.
- Medir antes y después ayuda a evitar optimizaciones innecesarias.

### Preguntas sobre índices

- ¿Por qué no siempre mejora el tiempo cuando una tabla tiene pocos registros?
- ¿Qué significa medir antes de optimizar?

## 7. Vistas y vistas materializadas

Script: `sql/07_vistas.sql`

Una vista guarda una consulta con nombre. Ayuda a reutilizar lógica y mejorar
legibilidad. Una vista materializada guarda físicamente el resultado y debe
refrescarse cuando cambian los datos.

### Qué observar en vistas

- Una vista común simplifica consultas frecuentes.
- Una vista materializada puede mejorar lecturas repetidas, pero requiere
  `REFRESH`.
- PostgreSQL no usa `CREATE OR REPLACE MATERIALIZED VIEW`; por eso se elimina
  y recrea.

### Preguntas sobre vistas

- ¿Una vista común mejora rendimiento o legibilidad?
- ¿Qué diferencia hay entre una vista y una vista materializada?

## 8. JSONB para parámetros variables

Script: `sql/08_jsonb_parametros.sql`

La tabla `experimentos_modelos` ya tiene una columna `parametros` de tipo
`TEXT`. Para no romper el diseño anterior, la Clase 3 agrega una nueva columna
`parametros_jsonb`.

`JSONB` permite guardar parámetros variables cuando distintos modelos tienen
configuraciones distintas.

### Qué observar en JSONB

- `parametros_jsonb ->> 'criterion'` extrae un valor como texto.
- `parametros_jsonb ? 'criterion'` pregunta si existe una clave.
- `parametros_jsonb @> '{"criterion": "gini"}'` busca documentos que contienen
  un fragmento JSON.
- Un índice `GIN` puede ayudar en búsquedas sobre JSONB.

### Preguntas sobre JSONB

- ¿Por qué algunos parámetros de modelos conviene guardarlos como `JSONB`?
- ¿Cuándo no conviene usar `JSONB`?

## 9. Desafíos

Script: `sql/09_practica.sql`

El último archivo propone ejercicios para resolver. Algunos están parcialmente
guiados y otros quedan abiertos.

### Qué observar en desafíos

- Si podés explicar la relación entre tablas antes de escribir el SQL, la
  consulta sale más fácil.
- Los desafíos combinan lo visto: `JOIN`, agregaciones, ventanas, vistas y
  `JSONB`.

### Preguntas de cierre

- ¿Qué consultas ayudan a analizar la calidad de los modelos?
- ¿Qué parte del diseño cambiarías si el caso creciera?
- ¿Qué conviene dejar como tabla relacional y qué podría ser flexible con
  `JSONB`?
