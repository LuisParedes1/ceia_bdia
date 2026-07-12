-- ============================================================
-- Script 05
-- Subconsultas y funciones de ventana.
--
-- Las subconsultas permiten comparar contra resultados calculados.
-- Las funciones de ventana calculan valores agregados sin perder
-- el detalle de cada fila.
-- ============================================================

-- ============================================================
-- 1. Métricas accuracy superiores al promedio de accuracy
--
-- La subconsulta calcula el promedio. La consulta principal trae
-- las métricas que superan ese valor.
-- ============================================================

SELECT
    mt.id,
    mt.experimento_id,
    mt.nombre AS metrica,
    mt.valor
FROM metricas AS mt
WHERE mt.nombre = 'accuracy'
  AND mt.valor > (
      SELECT AVG(valor)
      FROM metricas
      WHERE nombre = 'accuracy'
  )
ORDER BY mt.valor DESC;

-- ============================================================
-- 2. Modelos que participaron en experimentos
--
-- IN compara modelos.id contra los modelo_id existentes en la
-- tabla intermedia experimentos_modelos.
-- ============================================================

SELECT
    m.id,
    m.nombre,
    tm.nombre AS tipo_modelo,
    m.version
FROM modelos AS m
JOIN tipos_modelo AS tm
    ON tm.id = m.tipo_modelo_id
WHERE m.id IN (
    SELECT em.modelo_id
    FROM experimentos_modelos AS em
)
ORDER BY m.nombre;

-- ============================================================
-- 3. ROW_NUMBER para rankear métricas por nombre
--
-- PARTITION BY crea un ranking separado para cada tipo de métrica.
-- No se pierden filas: cada métrica sigue apareciendo en el resultado.
-- ============================================================

SELECT
    mt.nombre AS metrica,
    mt.experimento_id,
    mt.valor,
    ROW_NUMBER() OVER (
        PARTITION BY mt.nombre
        ORDER BY mt.valor DESC
    ) AS posicion_en_su_metrica
FROM metricas AS mt
ORDER BY mt.nombre, posicion_en_su_metrica;

-- ============================================================
-- 4. AVG OVER para comparar cada métrica contra su promedio
--
-- A diferencia de GROUP BY, la función de ventana conserva cada fila
-- y agrega el promedio del grupo como una columna más.
-- ============================================================

SELECT
    mt.nombre AS metrica,
    mt.experimento_id,
    mt.valor,
    AVG(mt.valor) OVER (PARTITION BY mt.nombre) AS promedio_de_la_metrica,
    mt.valor - AVG(mt.valor) OVER (PARTITION BY mt.nombre) AS diferencia_vs_promedio
FROM metricas AS mt
ORDER BY mt.nombre, mt.valor DESC;

-- ============================================================
-- 5. DENSE_RANK para comparar modelos según accuracy
--
-- DENSE_RANK asigna la misma posición a empates y no deja huecos.
-- ============================================================

SELECT
    m.nombre AS modelo,
    tm.nombre AS tipo_modelo,
    e.nombre AS experimento,
    mt.valor AS accuracy,
    DENSE_RANK() OVER (
        ORDER BY mt.valor DESC
    ) AS ranking_accuracy
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
ORDER BY ranking_accuracy, modelo;
