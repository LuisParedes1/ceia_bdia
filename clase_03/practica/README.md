# BDIA - Práctica Clase 3

Tema: Diseño relacional, consultas intermedias y optimización en PostgreSQL.

Esta práctica continúa el caso guía iniciado en `clase_02/practica`:
usuarios, datasets, modelos, experimentos, experimentos_modelos y metricas.

La pregunta que guía la clase es:

> ¿Cómo pasamos de una base que guarda datos a una base que permite analizar
> experimentos de IA?

## Objetivos

- Normalizar columnas de texto libre en tablas catálogo.
- Revisar el esquema relacional existente.
- Consultar datos combinando varias tablas con `JOIN`.
- Construir indicadores con `GROUP BY` y `HAVING`.
- Usar subconsultas y funciones de ventana.
- Medir consultas con `EXPLAIN ANALYZE`.
- Crear índices y comparar planes de ejecución.
- Crear vistas y vistas materializadas.
- Usar `JSONB` para representar parámetros variables de modelos.

## Requisito previo

Antes de comenzar, ejecutá la práctica de Clase 2 en este orden:

1. `01_crear_tablas.sql`
2. `02_insertar_datos.sql`
3. `03_consultas_basicas.sql`
4. `04_validar_restricciones.sql`

La Clase 3 no define un nuevo `docker-compose.yml`. Reutiliza el entorno de
`clase_02/practica`.

Para levantar PostgreSQL y pgAdmin:

```bash
cd clase_02/practica
docker compose up -d
```

Después, entrá a pgAdmin y ejecutá los scripts de `clase_03/practica/sql/`
desde **Query Tool**.

## Datos adicionales para Clase 3

El script `00_poblar_datos_clase_03.sql` agrega más usuarios, datasets,
modelos, experimentos y métricas para que las consultas analíticas tengan más
sentido.

Este script no reemplaza los datos de Clase 2 ni borra tablas. Solo amplía la
base existente. Está pensado para ejecutarse una sola vez sobre una base limpia
ya cargada con los datos de Clase 2.

## Orden sugerido de ejecución

1. `00_poblar_datos_clase_03.sql`
2. `01_normalizacion.sql`
3. `02_revisar_esquema.sql`
4. `03_consultas_joins.sql`
5. `04_agregaciones_rankings.sql`
6. `05_subconsultas_ventanas.sql`
7. `06_explain_indices.sql`
8. `07_vistas.sql`
9. `08_jsonb_parametros.sql`
10. `09_practica.sql`

## Qué vas a practicar

En Clase 2 la base empezó guardando datos y validando reglas básicas. En
Clase 3 usamos esa misma base para normalizar columnas de texto libre,
conectar entidades, resumir información, comparar resultados, medir
consultas y mejorar el diseño sin romper lo existente.

La progresión esperada es:

1. Normalizar columnas de texto libre en tablas catálogo.
2. Revisar el diseño resultante.
3. Cruzar tablas.
4. Construir indicadores.
5. Comparar valores con subconsultas y ventanas.
6. Medir consultas.
7. Crear índices.
8. Reutilizar consultas con vistas.
9. Usar `JSONB` para parámetros flexibles.
10. Resolver desafíos.
