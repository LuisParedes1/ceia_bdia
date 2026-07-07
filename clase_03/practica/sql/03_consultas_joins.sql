-- ============================================================
-- Script 03
-- Consultas con JOIN.
--
-- Un JOIN combina filas de distintas tablas usando una condición
-- de relación. En este caso usamos las claves foráneas creadas en
-- Clase 2, más las de tipos_fuente y tipos_modelo agregadas por el
-- ejercicio de normalización (sql/01_normalizacion.sql).
-- ============================================================

-- ============================================================
-- 1. Datasets cargados por cada usuario
--
-- usuarios.id se conecta con datasets.usuario_id.
-- tipos_fuente.id se conecta con datasets.tipo_fuente_id.
-- ============================================================

SELECT
    u.id AS usuario_id,
    u.nombre AS usuario,
    u.email,
    d.id AS dataset_id,
    d.nombre AS dataset,
    tf.nombre AS tipo_fuente,
    d.fuente_detalle,
    d.cantidad_registros
FROM usuarios AS u
JOIN datasets AS d
    ON d.usuario_id = u.id
JOIN tipos_fuente AS tf
    ON tf.id = d.tipo_fuente_id
ORDER BY u.nombre, d.nombre;

-- ============================================================
-- 2. Experimentos asociados a cada dataset
--
-- datasets.id se conecta con experimentos.dataset_id.
-- ============================================================

SELECT
    d.id AS dataset_id,
    d.nombre AS dataset,
    tf.nombre AS tipo_fuente,
    d.fuente_detalle,
    e.id AS experimento_id,
    e.nombre AS experimento,
    e.fecha,
    e.finalizado
FROM datasets AS d
JOIN tipos_fuente AS tf
    ON tf.id = d.tipo_fuente_id
JOIN experimentos AS e
    ON e.dataset_id = d.id
ORDER BY d.nombre, e.fecha;

-- ============================================================
-- 3. Modelos usados en cada experimento
--
-- La tabla experimentos_modelos conecta experimentos y modelos.
-- Esta tabla intermedia existe porque la relación es muchos a muchos.
-- tipos_modelo.id se conecta con modelos.tipo_modelo_id.
-- ============================================================

SELECT
    e.id AS experimento_id,
    e.nombre AS experimento,
    m.id AS modelo_id,
    m.nombre AS modelo,
    tm.nombre AS tipo_modelo,
    m.version,
    em.parametros,
    em.resultado
FROM experimentos AS e
JOIN experimentos_modelos AS em
    ON em.experimento_id = e.id
JOIN modelos AS m
    ON m.id = em.modelo_id
JOIN tipos_modelo AS tm
    ON tm.id = m.tipo_modelo_id
ORDER BY e.nombre, m.nombre;

-- ============================================================
-- 4. Métricas obtenidas por experimento
--
-- experimentos.id se conecta con metricas.experimento_id.
-- ============================================================

SELECT
    e.id AS experimento_id,
    e.nombre AS experimento,
    e.finalizado,
    mt.nombre AS metrica,
    mt.valor,
    mt.fecha_registro
FROM experimentos AS e
JOIN metricas AS mt
    ON mt.experimento_id = e.id
ORDER BY e.nombre, mt.nombre;

-- ============================================================
-- 5. Consulta completa del caso guía
--
-- Esta consulta recorre el camino:
-- usuarios -> datasets -> experimentos -> experimentos_modelos
-- -> modelos, y además suma las métricas del experimento.
-- ============================================================

SELECT
    u.nombre AS usuario,
    u.email,
    d.nombre AS dataset,
    tf.nombre AS tipo_fuente,
    e.nombre AS experimento,
    e.fecha,
    e.finalizado,
    m.nombre AS modelo,
    tm.nombre AS tipo_modelo,
    em.parametros,
    em.resultado,
    mt.nombre AS metrica,
    mt.valor
FROM usuarios AS u
JOIN datasets AS d
    ON d.usuario_id = u.id
JOIN tipos_fuente AS tf
    ON tf.id = d.tipo_fuente_id
JOIN experimentos AS e
    ON e.dataset_id = d.id
JOIN experimentos_modelos AS em
    ON em.experimento_id = e.id
JOIN modelos AS m
    ON m.id = em.modelo_id
JOIN tipos_modelo AS tm
    ON tm.id = m.tipo_modelo_id
JOIN metricas AS mt
    ON mt.experimento_id = e.id
ORDER BY u.nombre, d.nombre, e.nombre, m.nombre, mt.nombre;

-- ============================================================
-- 6. LEFT JOIN para detectar usuarios sin datasets
--
-- LEFT JOIN conserva las filas de la tabla izquierda aunque no
-- tengan coincidencia en la tabla derecha.
-- ============================================================

SELECT
    u.id AS usuario_id,
    u.nombre AS usuario,
    u.email
FROM usuarios AS u
LEFT JOIN datasets AS d
    ON d.usuario_id = u.id
WHERE d.id IS NULL
ORDER BY u.nombre;

-- ============================================================
-- 7. LEFT JOIN para detectar datasets sin experimentos
-- ============================================================

SELECT
    d.id AS dataset_id,
    d.nombre AS dataset,
    d.fuente_detalle
FROM datasets AS d
LEFT JOIN experimentos AS e
    ON e.dataset_id = d.id
WHERE e.id IS NULL
ORDER BY d.nombre;
