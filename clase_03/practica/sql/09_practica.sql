-- ============================================================
-- Script 09
-- Ejercicios de práctica.
--
-- Este archivo contiene consignas para resolver después de ejecutar
-- los scripts anteriores. Algunas consultas están parcialmente guiadas
-- y otras quedan abiertas.
--
-- Recomendación: ejecutá cada bloque por separado en pgAdmin.
-- ============================================================

-- ============================================================
-- Desafío 1
-- Listar usuarios, datasets y cantidad de experimentos por dataset.
--
-- Pistas:
-- - usuarios se conecta con datasets.
-- - datasets se conecta con experimentos.
-- - COUNT(e.id) cuenta experimentos.
-- ============================================================

SELECT
    u.nombre AS usuario,
    d.nombre AS dataset,
    COUNT(e.id) AS cantidad_experimentos
FROM usuarios AS u
JOIN datasets AS d
    ON d.usuario_id = u.id
LEFT JOIN experimentos AS e
    ON e.dataset_id = d.id
GROUP BY u.nombre, d.nombre
ORDER BY usuario, dataset;

-- ============================================================
-- Desafío 2
-- Mostrar el mejor valor de accuracy registrado y el experimento asociado.
--
-- Completá la consulta.
-- ============================================================

-- SELECT
--     e.nombre AS experimento,
--     mt.valor AS accuracy
-- FROM experimentos AS e
-- JOIN metricas AS mt
--     ON mt.experimento_id = e.id
-- WHERE mt.nombre = 'accuracy'
-- ORDER BY mt.valor DESC
-- LIMIT 1;

-- ============================================================
-- Desafío 3
-- Mostrar modelos que participaron en experimentos finalizados.
--
-- Pistas:
-- - experimentos.finalizado indica si terminó.
-- - experimentos_modelos conecta experimentos con modelos.
-- ============================================================

-- SELECT DISTINCT
--     m.nombre AS modelo,
--     tm.nombre AS tipo_modelo,
--     e.nombre AS experimento
-- FROM modelos AS m
-- JOIN tipos_modelo AS tm
--     ON tm.id = m.tipo_modelo_id
-- JOIN experimentos_modelos AS em
--     ON em.modelo_id = m.id
-- JOIN experimentos AS e
--     ON e.id = em.experimento_id
-- WHERE e.finalizado = TRUE
-- ORDER BY modelo;

-- ============================================================
-- Desafío 4
-- Crear una vista que muestre usuario, dataset, experimento, modelo,
-- métrica y valor.
--
-- Completá los JOIN necesarios.
-- ============================================================

-- CREATE OR REPLACE VIEW vw_caso_guia_completo AS
-- SELECT
--     u.nombre AS usuario,
--     d.nombre AS dataset,
--     e.nombre AS experimento,
--     m.nombre AS modelo,
--     mt.nombre AS metrica,
--     mt.valor
-- FROM usuarios AS u
-- JOIN datasets AS d
--     ON d.usuario_id = u.id
-- JOIN experimentos AS e
--     ON e.dataset_id = d.id
-- JOIN experimentos_modelos AS em
--     ON em.experimento_id = e.id
-- JOIN modelos AS m
--     ON m.id = em.modelo_id
-- JOIN metricas AS mt
--     ON mt.experimento_id = e.id;
--
-- SELECT *
-- FROM vw_caso_guia_completo
-- ORDER BY usuario, dataset, experimento, modelo, metrica;

-- ============================================================
-- Desafío 5
-- Guardar parámetros JSONB para un nuevo modelo y consultar uno de
-- sus campos internos.
--
-- Este desafío está guiado, pero no completamente resuelto.
-- Adaptá los ids según los datos que tengas en tu base.
-- ============================================================

-- INSERT INTO modelos(usuario_id, nombre, tipo_modelo_id, version)
-- VALUES (
--     1,
--     'Modelo experimental JSONB',
--     (SELECT id FROM tipos_modelo WHERE nombre = 'Clasificación'),
--     'v2'
-- );
--
-- INSERT INTO experimentos_modelos(experimento_id, modelo_id, parametros, resultado, parametros_jsonb)
-- VALUES (
--     1,
--     -- Reemplazar por el id real del modelo insertado.
--     999,
--     'configuracion flexible',
--     'Pendiente de evaluación',
--     '{"learning_rate": 0.01, "regularization": "l2"}'::jsonb
-- );
--
-- SELECT
--     modelo_id,
--     parametros_jsonb ->> 'learning_rate' AS learning_rate
-- FROM experimentos_modelos
-- WHERE parametros_jsonb ? 'learning_rate';

-- ============================================================
-- Desafío 6
-- Detectar datasets sin experimentos.
--
-- Pista: usar LEFT JOIN y filtrar donde e.id IS NULL.
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

-- ============================================================
-- Desafío 7
-- Ranking de modelos por alguna métrica.
--
-- Elegí una métrica, por ejemplo accuracy, y ordená los modelos por
-- el valor obtenido. Podés usar ROW_NUMBER, RANK o DENSE_RANK.
-- ============================================================

-- SELECT
--     m.nombre AS modelo,
--     mt.nombre AS metrica,
--     mt.valor,
--     ROW_NUMBER() OVER (ORDER BY mt.valor DESC) AS ranking
-- FROM modelos AS m
-- JOIN experimentos_modelos AS em
--     ON em.modelo_id = m.id
-- JOIN metricas AS mt
--     ON mt.experimento_id = em.experimento_id
-- WHERE mt.nombre = 'accuracy'
-- ORDER BY ranking;

-- ============================================================
-- Desafío 8
-- Pregunta abierta
--
-- ¿Qué consulta escribirías para decidir qué dataset conviene usar
-- como base para próximos experimentos?
--
-- Escribí tu consulta debajo.
-- ============================================================

-- Tu consulta:
