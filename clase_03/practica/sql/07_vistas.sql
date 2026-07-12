-- ============================================================
-- Script 07
-- Vistas y vistas materializadas.
--
-- Una vista guarda una consulta con nombre. Ayuda a reutilizar
-- consultas y mejorar legibilidad.
--
-- Una vista materializada guarda físicamente el resultado. Puede
-- acelerar lecturas repetidas, pero debe actualizarse con REFRESH.
-- ============================================================

-- ============================================================
-- 1. Vista resumen de experimentos
--
-- CREATE OR REPLACE permite ejecutar el script varias veces sin
-- tener que borrar la vista manualmente.
-- ============================================================

CREATE OR REPLACE VIEW vw_experimentos_resumen AS
SELECT
    e.id AS experimento_id,
    e.nombre AS experimento,
    e.fecha,
    e.finalizado,
    d.id AS dataset_id,
    d.nombre AS dataset,
    tf.nombre AS tipo_fuente,
    d.fuente_detalle,
    u.id AS usuario_id,
    u.nombre AS usuario,
    u.email
FROM experimentos AS e
JOIN datasets AS d
    ON d.id = e.dataset_id
JOIN tipos_fuente AS tf
    ON tf.id = d.tipo_fuente_id
JOIN usuarios AS u
    ON u.id = d.usuario_id;

-- Consultar la vista como si fuera una tabla.
SELECT *
FROM vw_experimentos_resumen
ORDER BY usuario, dataset, experimento;

-- ============================================================
-- 2. Vista resumen de experimentos y modelos
--
-- Incluye la asociación muchos a muchos entre experimentos y modelos.
-- ============================================================

CREATE OR REPLACE VIEW vw_experimentos_modelos_resumen AS
SELECT
    e.id AS experimento_id,
    e.nombre AS experimento,
    d.nombre AS dataset,
    m.id AS modelo_id,
    m.nombre AS modelo,
    tm.nombre AS tipo_modelo,
    em.parametros,
    em.resultado
FROM experimentos AS e
JOIN datasets AS d
    ON d.id = e.dataset_id
JOIN experimentos_modelos AS em
    ON em.experimento_id = e.id
JOIN modelos AS m
    ON m.id = em.modelo_id
JOIN tipos_modelo AS tm
    ON tm.id = m.tipo_modelo_id;

-- Consultar la segunda vista.
SELECT *
FROM vw_experimentos_modelos_resumen
ORDER BY dataset, experimento, modelo;

-- ============================================================
-- 3. Vista materializada con promedios de métricas
--
-- PostgreSQL no permite CREATE OR REPLACE MATERIALIZED VIEW.
-- Por eso se elimina si existe y se vuelve a crear.
-- ============================================================

DROP MATERIALIZED VIEW IF EXISTS mv_metricas_promedio;

CREATE MATERIALIZED VIEW mv_metricas_promedio AS
SELECT
    mt.nombre AS metrica,
    AVG(mt.valor) AS promedio,
    MIN(mt.valor) AS minimo,
    MAX(mt.valor) AS maximo,
    COUNT(*) AS cantidad_registros
FROM metricas AS mt
GROUP BY mt.nombre;

-- Actualizar la vista materializada.
-- En este punto no cambia nada porque se acaba de crear, pero queda
-- el comando para practicar el flujo correcto.
REFRESH MATERIALIZED VIEW mv_metricas_promedio;

-- Consultar la vista materializada.
SELECT *
FROM mv_metricas_promedio
ORDER BY metrica;
