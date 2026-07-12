-- ============================================================
-- Script 06
-- EXPLAIN ANALYZE e índices.
--
-- EXPLAIN ANALYZE muestra el plan elegido por PostgreSQL y ejecuta
-- la consulta para medir tiempos reales.
--
-- Importante: con tablas chicas, PostgreSQL puede seguir usando
-- Seq Scan aunque exista un índice. Eso no significa que el índice
-- esté mal; significa que leer toda la tabla puede ser más barato.
-- ============================================================

-- ============================================================
-- 1. Medir una consulta filtrando métricas por nombre
-- ============================================================

EXPLAIN ANALYZE
SELECT *
FROM metricas
WHERE nombre = 'accuracy';

-- ============================================================
-- 2. Crear índice sobre metricas(nombre)
--
-- IF NOT EXISTS evita error si el índice ya fue creado en una
-- ejecución anterior.
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_metricas_nombre
ON metricas(nombre);

-- Repetir la medición para comparar el plan.
EXPLAIN ANALYZE
SELECT *
FROM metricas
WHERE nombre = 'accuracy';

-- ============================================================
-- 3. Medir un JOIN entre usuarios y datasets
-- ============================================================

EXPLAIN ANALYZE
SELECT
    u.nombre AS usuario,
    d.nombre AS dataset,
    d.fuente_detalle
FROM usuarios AS u
JOIN datasets AS d
    ON d.usuario_id = u.id
WHERE u.email = 'ana@example.com';

-- ============================================================
-- 4. Crear índice sobre datasets(usuario_id)
--
-- Este índice puede ayudar cuando se buscan datasets de un usuario
-- o cuando el JOIN necesita recorrer muchos datasets.
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_datasets_usuario_id
ON datasets(usuario_id);

-- Repetir la medición para comparar el plan.
EXPLAIN ANALYZE
SELECT
    u.nombre AS usuario,
    d.nombre AS dataset,
    d.fuente_detalle
FROM usuarios AS u
JOIN datasets AS d
    ON d.usuario_id = u.id
WHERE u.email = 'ana@example.com';

-- ============================================================
-- 5. Bloque opcional para generar más datos de prueba
--
-- NO se ejecuta automáticamente porque está comentado.
-- Si querés observar mejor el impacto de los índices, podés copiar
-- este bloque, descomentarlo y ejecutarlo en una base de práctica.
-- ============================================================

-- INSERT INTO metricas(experimento_id, nombre, valor)
-- SELECT
--     1 AS experimento_id,
--     CASE
--         WHEN gs % 3 = 0 THEN 'accuracy'
--         WHEN gs % 3 = 1 THEN 'precision'
--         ELSE 'recall'
--     END AS nombre,
--     ROUND((0.50 + random() * 0.50)::numeric, 4) AS valor
-- FROM generate_series(1, 10000) AS gs;
--
-- ANALYZE metricas;
--
-- EXPLAIN ANALYZE
-- SELECT *
-- FROM metricas
-- WHERE nombre = 'accuracy';
