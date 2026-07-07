-- ============================================================
-- Script 02
-- Revisar el esquema existente.
--
-- Clase 3 - Diseño relacional, consultas intermedias y
-- optimización en PostgreSQL.
--
-- Este script no modifica datos. Sirve para recordar qué tablas
-- creó la práctica de Clase 2, qué agregó el ejercicio de
-- normalización (sql/01_normalizacion.sql) y cómo se conectan.
-- ============================================================

-- ============================================================
-- 1. Revisar datos cargados
--
-- Cada SELECT muestra el contenido actual de una tabla principal.
-- Si alguna tabla aparece vacía, revisá que se hayan ejecutado los
-- scripts 01 y 02 de la práctica de Clase 2.
-- ============================================================

SELECT *
FROM usuarios;

SELECT *
FROM datasets;

SELECT *
FROM tipos_fuente;

SELECT *
FROM modelos;

SELECT *
FROM tipos_modelo;

SELECT *
FROM experimentos;

SELECT *
FROM experimentos_modelos;

SELECT *
FROM metricas;

-- ============================================================
-- 2. Revisar columnas y tipos de datos
--
-- information_schema.columns permite inspeccionar el diseño desde
-- SQL: nombres de columnas, tipos y si aceptan NULL.
-- ============================================================

SELECT
    table_name,
    ordinal_position,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name IN (
      'usuarios',
      'datasets',
      'tipos_fuente',
      'modelos',
      'tipos_modelo',
      'experimentos',
      'experimentos_modelos',
      'metricas'
  )
ORDER BY table_name, ordinal_position;

-- ============================================================
-- 3. Revisar restricciones principales
--
-- Las constraints expresan reglas del modelo: claves primarias,
-- claves foráneas, valores únicos y validaciones CHECK.
-- ============================================================

SELECT
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
LEFT JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
   AND tc.table_schema = kcu.table_schema
LEFT JOIN information_schema.constraint_column_usage AS ccu
    ON tc.constraint_name = ccu.constraint_name
   AND tc.table_schema = ccu.table_schema
WHERE tc.table_schema = 'public'
  AND tc.table_name IN (
      'usuarios',
      'datasets',
      'tipos_fuente',
      'modelos',
      'tipos_modelo',
      'experimentos',
      'experimentos_modelos',
      'metricas'
  )
ORDER BY tc.table_name, tc.constraint_type, tc.constraint_name;

-- ============================================================
-- 4. Mapa conceptual de relaciones
--
-- usuarios 1:N datasets
--   usuarios.id se referencia desde datasets.usuario_id
--
-- tipos_fuente 1:N datasets
--   tipos_fuente.id se referencia desde datasets.tipo_fuente_id
--   (agregado por el ejercicio de normalización)
--
-- usuarios 1:N modelos
--   usuarios.id se referencia desde modelos.usuario_id
--
-- tipos_modelo 1:N modelos
--   tipos_modelo.id se referencia desde modelos.tipo_modelo_id
--   (agregado por el ejercicio de normalización)
--
-- datasets 1:N experimentos
--   datasets.id se referencia desde experimentos.dataset_id
--
-- experimentos N:M modelos
--   experimentos_modelos resuelve la relación con:
--   - experimentos_modelos.experimento_id
--   - experimentos_modelos.modelo_id
--
-- experimentos 1:N metricas
--   experimentos.id se referencia desde metricas.experimento_id
-- ============================================================
