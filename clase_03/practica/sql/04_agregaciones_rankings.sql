-- ============================================================
-- Script 04
-- Agregaciones y rankings.
--
-- GROUP BY agrupa filas para calcular indicadores.
-- WHERE filtra filas antes de agrupar.
-- HAVING filtra grupos después de agrupar.
-- ============================================================

-- ============================================================
-- 1. Cantidad de datasets por usuario
--
-- LEFT JOIN permite incluir usuarios que todavía no tengan datasets.
-- ============================================================

SELECT
    u.id AS usuario_id,
    u.nombre AS usuario,
    COUNT(d.id) AS cantidad_datasets
FROM usuarios AS u
LEFT JOIN datasets AS d
    ON d.usuario_id = u.id
GROUP BY u.id, u.nombre
ORDER BY cantidad_datasets DESC, usuario;

-- ============================================================
-- 2. Cantidad de experimentos por dataset
--
-- Este indicador ayuda a ver qué datasets se están usando más.
-- ============================================================

SELECT
    d.id AS dataset_id,
    d.nombre AS dataset,
    COUNT(e.id) AS cantidad_experimentos
FROM datasets AS d
LEFT JOIN experimentos AS e
    ON e.dataset_id = d.id
GROUP BY d.id, d.nombre
ORDER BY cantidad_experimentos DESC, dataset;

-- ============================================================
-- 3. Promedio, mínimo, máximo y cantidad por tipo de métrica
--
-- Cada nombre de métrica forma un grupo: accuracy, precision,
-- recall, f1_score, mae, etc.
-- ============================================================

SELECT
    mt.nombre AS metrica,
    AVG(mt.valor) AS promedio,
    MIN(mt.valor) AS minimo,
    MAX(mt.valor) AS maximo,
    COUNT(*) AS cantidad_registros
FROM metricas AS mt
GROUP BY mt.nombre
ORDER BY mt.nombre;

-- ============================================================
-- 4. Datasets con al menos cierta cantidad de experimentos
--
-- HAVING se usa porque el filtro depende de COUNT(e.id), que es
-- un cálculo agregado.
-- ============================================================

SELECT
    d.id AS dataset_id,
    d.nombre AS dataset,
    COUNT(e.id) AS cantidad_experimentos
FROM datasets AS d
LEFT JOIN experimentos AS e
    ON e.dataset_id = d.id
GROUP BY d.id, d.nombre
HAVING COUNT(e.id) >= 1
ORDER BY cantidad_experimentos DESC, dataset;

-- ============================================================
-- 5. Promedio de accuracy por modelo
--
-- La métrica pertenece al experimento. Para asociarla al modelo,
-- recorremos experimentos -> experimentos_modelos -> modelos.
-- ============================================================

SELECT
    m.id AS modelo_id,
    m.nombre AS modelo,
    tm.nombre AS tipo_modelo,
    AVG(mt.valor) AS accuracy_promedio,
    COUNT(mt.id) AS cantidad_metricas_accuracy
FROM modelos AS m
JOIN tipos_modelo AS tm
    ON tm.id = m.tipo_modelo_id
JOIN experimentos_modelos AS em
    ON em.modelo_id = m.id
JOIN experimentos AS e
    ON e.id = em.experimento_id
JOIN metricas AS mt
    ON mt.experimento_id = e.id
WHERE mt.nombre = 'accuracy'
GROUP BY m.id, m.nombre, tm.nombre
ORDER BY accuracy_promedio DESC;

-- ============================================================
-- 6. Ranking simple de datasets por cantidad de registros
--
-- ORDER BY permite ordenar el indicador calculado o una columna
-- del dataset para construir rankings básicos.
-- ============================================================

SELECT
    d.nombre AS dataset,
    d.fuente_detalle,
    d.cantidad_registros
FROM datasets AS d
ORDER BY d.cantidad_registros DESC NULLS LAST;
