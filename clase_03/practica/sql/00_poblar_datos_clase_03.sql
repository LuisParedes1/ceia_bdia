-- ============================================================
-- Script 00
-- Poblar más datos para la práctica de Clase 3.
--
-- Este script amplía los datos creados en Clase 2 para que las
-- consultas con JOIN, agregaciones, rankings, ventanas e índices
-- tengan resultados más interesantes.
--
-- Importante:
-- - Ejecutar después de Clase 2: 01_crear_tablas.sql y
--   02_insertar_datos.sql.
-- - No borra ni modifica la estructura existente.
-- - Está pensado para ejecutarse una sola vez sobre una base limpia
--   ya cargada con los datos de Clase 2.
-- ============================================================

-- ============================================================
-- 1. Insertar usuarios adicionales
-- ============================================================

INSERT INTO usuarios(nombre, email)
VALUES
    ('Carla Ruiz', 'carla@example.com'),
    ('Diego Fernández', 'diego@example.com'),
    ('Sofía Herrera', 'sofia@example.com'),
    ('Invitado sin carga', 'invitado@example.com');

-- ============================================================
-- 2. Insertar datasets adicionales
--
-- usuario_id referencia a usuarios(id). Para no depender del número
-- exacto que asignó SERIAL, buscamos el id por email.
-- ============================================================

INSERT INTO datasets(usuario_id, nombre, fuente, cantidad_registros)
VALUES
    (
        (SELECT id FROM usuarios WHERE email = 'carla@example.com'),
        'Sensores industriales',
        'IoT industrial',
        42000
    ),
    (
        (SELECT id FROM usuarios WHERE email = 'diego@example.com'),
        'Transacciones bancarias',
        'Sistema financiero',
        120000
    ),
    (
        (SELECT id FROM usuarios WHERE email = 'sofia@example.com'),
        'Tickets de soporte',
        'Mesa de ayuda',
        18000
    ),
    (
        (SELECT id FROM usuarios WHERE email = 'sofia@example.com'),
        'Audios de soporte',
        'Call center',
        9000
    ),
    (
        (SELECT id FROM usuarios WHERE email = 'ana@example.com'),
        'Clima histórico regional',
        'Servicio meteorológico',
        65000
    );

-- ============================================================
-- 3. Insertar modelos adicionales
--
-- Cada modelo pertenece a un usuario.
-- ============================================================

INSERT INTO modelos(usuario_id, nombre, tipo, version)
VALUES
    (
        (SELECT id FROM usuarios WHERE email = 'carla@example.com'),
        'Clasificador industrial',
        'Clasificación',
        'v1'
    ),
    (
        (SELECT id FROM usuarios WHERE email = 'diego@example.com'),
        'Detector de fraude',
        'Clasificación',
        'v2'
    ),
    (
        (SELECT id FROM usuarios WHERE email = 'diego@example.com'),
        'Segmentador de clientes',
        'Clustering',
        'v1'
    ),
    (
        (SELECT id FROM usuarios WHERE email = 'sofia@example.com'),
        'Clasificador de tickets',
        'Clasificación',
        'v1'
    ),
    (
        (SELECT id FROM usuarios WHERE email = 'ana@example.com'),
        'Pronóstico climático',
        'Regresión',
        'v2'
    );

-- ============================================================
-- 4. Insertar experimentos adicionales
--
-- dataset_id referencia a datasets(id). Buscamos el dataset por nombre
-- para que el script sea fácil de leer en clase.
-- ============================================================

INSERT INTO experimentos(dataset_id, nombre, descripcion, finalizado)
VALUES
    (
        (SELECT id FROM datasets WHERE nombre = 'Clima histórico regional'),
        'Experimento lluvia v2',
        'Segunda prueba para predecir lluvia con más datos históricos.',
        TRUE
    ),
    (
        (SELECT id FROM datasets WHERE nombre = 'Sensores industriales'),
        'Experimento industrial v1',
        'Clasificación de eventos anómalos en sensores industriales.',
        TRUE
    ),
    (
        (SELECT id FROM datasets WHERE nombre = 'Transacciones bancarias'),
        'Experimento fraude v1',
        'Detección inicial de posibles transacciones fraudulentas.',
        TRUE
    ),
    (
        (SELECT id FROM datasets WHERE nombre = 'Transacciones bancarias'),
        'Experimento fraude v2',
        'Ajuste de parámetros para mejorar recall en fraude.',
        FALSE
    ),
    (
        (SELECT id FROM datasets WHERE nombre = 'Tickets de soporte'),
        'Experimento tickets v1',
        'Clasificación automática de tickets por prioridad.',
        TRUE
    ),
    (
        (SELECT id FROM datasets WHERE nombre = 'Tickets de soporte'),
        'Experimento tickets v2',
        'Comparación de métricas luego de balancear clases.',
        FALSE
    );

-- ============================================================
-- 5. Asociar experimentos con modelos
--
-- Esta tabla representa la relación muchos a muchos entre
-- experimentos y modelos.
-- ============================================================

INSERT INTO experimentos_modelos(experimento_id, modelo_id, parametros, resultado)
VALUES
    (
        (SELECT id FROM experimentos WHERE nombre = 'Experimento lluvia v2'),
        (SELECT id FROM modelos WHERE nombre = 'Pronóstico climático'),
        'max_depth=8;criterion=gini',
        'Mejora contra la versión inicial'
    ),
    (
        (SELECT id FROM experimentos WHERE nombre = 'Experimento industrial v1'),
        (SELECT id FROM modelos WHERE nombre = 'Clasificador industrial'),
        'max_depth=6;criterion=entropy',
        'Buen desempeño en eventos frecuentes'
    ),
    (
        (SELECT id FROM experimentos WHERE nombre = 'Experimento fraude v1'),
        (SELECT id FROM modelos WHERE nombre = 'Detector de fraude'),
        'threshold=0.65;class_weight=balanced',
        'Alta precisión inicial'
    ),
    (
        (SELECT id FROM experimentos WHERE nombre = 'Experimento fraude v2'),
        (SELECT id FROM modelos WHERE nombre = 'Detector de fraude'),
        'threshold=0.45;class_weight=balanced',
        'Mejora recall, baja precisión'
    ),
    (
        (SELECT id FROM experimentos WHERE nombre = 'Experimento fraude v1'),
        (SELECT id FROM modelos WHERE nombre = 'Segmentador de clientes'),
        'n_clusters=4',
        'Segmentos útiles para análisis exploratorio'
    ),
    (
        (SELECT id FROM experimentos WHERE nombre = 'Experimento tickets v1'),
        (SELECT id FROM modelos WHERE nombre = 'Clasificador de tickets'),
        'max_features=5000',
        'Clasificación inicial aceptable'
    ),
    (
        (SELECT id FROM experimentos WHERE nombre = 'Experimento tickets v2'),
        (SELECT id FROM modelos WHERE nombre = 'Clasificador de tickets'),
        'max_features=8000;class_weight=balanced',
        'Modelo en evaluación'
    );

-- ============================================================
-- 6. Insertar métricas adicionales
--
-- Cada métrica pertenece a un experimento.
-- Sumamos varias métricas por experimento para que GROUP BY,
-- HAVING, rankings y ventanas produzcan resultados interesantes.
-- ============================================================

INSERT INTO metricas(experimento_id, nombre, valor)
VALUES
    ((SELECT id FROM experimentos WHERE nombre = 'Experimento lluvia v2'), 'accuracy', 0.86),
    ((SELECT id FROM experimentos WHERE nombre = 'Experimento lluvia v2'), 'precision', 0.83),
    ((SELECT id FROM experimentos WHERE nombre = 'Experimento lluvia v2'), 'recall', 0.81),
    ((SELECT id FROM experimentos WHERE nombre = 'Experimento lluvia v2'), 'f1_score', 0.82),

    ((SELECT id FROM experimentos WHERE nombre = 'Experimento industrial v1'), 'accuracy', 0.78),
    ((SELECT id FROM experimentos WHERE nombre = 'Experimento industrial v1'), 'precision', 0.76),
    ((SELECT id FROM experimentos WHERE nombre = 'Experimento industrial v1'), 'recall', 0.72),
    ((SELECT id FROM experimentos WHERE nombre = 'Experimento industrial v1'), 'f1_score', 0.74),

    ((SELECT id FROM experimentos WHERE nombre = 'Experimento fraude v1'), 'accuracy', 0.94),
    ((SELECT id FROM experimentos WHERE nombre = 'Experimento fraude v1'), 'precision', 0.96),
    ((SELECT id FROM experimentos WHERE nombre = 'Experimento fraude v1'), 'recall', 0.61),
    ((SELECT id FROM experimentos WHERE nombre = 'Experimento fraude v1'), 'f1_score', 0.75),

    ((SELECT id FROM experimentos WHERE nombre = 'Experimento fraude v2'), 'accuracy', 0.89),
    ((SELECT id FROM experimentos WHERE nombre = 'Experimento fraude v2'), 'precision', 0.82),
    ((SELECT id FROM experimentos WHERE nombre = 'Experimento fraude v2'), 'recall', 0.79),
    ((SELECT id FROM experimentos WHERE nombre = 'Experimento fraude v2'), 'f1_score', 0.80),

    ((SELECT id FROM experimentos WHERE nombre = 'Experimento tickets v1'), 'accuracy', 0.87),
    ((SELECT id FROM experimentos WHERE nombre = 'Experimento tickets v1'), 'precision', 0.84),
    ((SELECT id FROM experimentos WHERE nombre = 'Experimento tickets v1'), 'recall', 0.77),
    ((SELECT id FROM experimentos WHERE nombre = 'Experimento tickets v1'), 'f1_score', 0.80),

    ((SELECT id FROM experimentos WHERE nombre = 'Experimento tickets v2'), 'accuracy', 0.85),
    ((SELECT id FROM experimentos WHERE nombre = 'Experimento tickets v2'), 'precision', 0.79),
    ((SELECT id FROM experimentos WHERE nombre = 'Experimento tickets v2'), 'recall', 0.83),
    ((SELECT id FROM experimentos WHERE nombre = 'Experimento tickets v2'), 'f1_score', 0.81);

-- ============================================================
-- 7. Resumen rápido para verificar la carga
-- ============================================================

SELECT 'usuarios' AS tabla, COUNT(*) AS cantidad FROM usuarios
UNION ALL
SELECT 'datasets', COUNT(*) FROM datasets
UNION ALL
SELECT 'modelos', COUNT(*) FROM modelos
UNION ALL
SELECT 'experimentos', COUNT(*) FROM experimentos
UNION ALL
SELECT 'experimentos_modelos', COUNT(*) FROM experimentos_modelos
UNION ALL
SELECT 'metricas', COUNT(*) FROM metricas
ORDER BY tabla;
