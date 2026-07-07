-- ============================================================
-- Script 08
-- JSONB para parámetros variables de modelos.
--
-- En Clase 2 experimentos_modelos.parametros se creó como TEXT.
-- No reemplazamos esa columna para no romper lo ya construido.
-- En su lugar agregamos parametros_jsonb para mostrar una evolución
-- posible del diseño.
-- ============================================================

-- ============================================================
-- 1. Agregar columna JSONB
--
-- IF NOT EXISTS permite ejecutar el script más de una vez.
-- ============================================================

ALTER TABLE experimentos_modelos
ADD COLUMN IF NOT EXISTS parametros_jsonb JSONB;

-- ============================================================
-- 2. Cargar parámetros JSONB para distintos tipos de configuración
--
-- Usamos claves distintas porque cada modelo puede necesitar
-- parámetros diferentes.
-- ============================================================

-- Ejemplo tipo árbol de decisión: max_depth y criterion.
UPDATE experimentos_modelos AS em
SET parametros_jsonb = '{"max_depth": 5, "criterion": "gini"}'::jsonb
WHERE em.experimento_id = 1
  AND em.modelo_id = 1;

-- Ejemplo tipo red neuronal o modelo similar: epochs, batch_size y optimizer.
UPDATE experimentos_modelos AS em
SET parametros_jsonb = '{"epochs": 10, "batch_size": 32, "optimizer": "adam"}'::jsonb
WHERE em.experimento_id = 2
  AND em.modelo_id = 2;

-- Ejemplo de configuración experimental: test_size y random_state.
UPDATE experimentos_modelos AS em
SET parametros_jsonb = '{"test_size": 0.2, "random_state": 42}'::jsonb
WHERE em.experimento_id = 3
  AND em.modelo_id = 3;

-- Verificar los datos cargados.
SELECT
    experimento_id,
    modelo_id,
    parametros,
    parametros_jsonb
FROM experimentos_modelos
ORDER BY experimento_id, modelo_id;

-- ============================================================
-- 3. Consultar un campo interno con ->>
--
-- ->> devuelve el valor como texto.
-- ============================================================

SELECT
    experimento_id,
    modelo_id,
    parametros_jsonb ->> 'criterion' AS criterion
FROM experimentos_modelos
WHERE parametros_jsonb ->> 'criterion' IS NOT NULL;

-- ============================================================
-- 4. Consultar registros que tienen una clave
--
-- El operador ? pregunta si existe una clave dentro del JSONB.
-- ============================================================

SELECT
    experimento_id,
    modelo_id,
    parametros_jsonb
FROM experimentos_modelos
WHERE parametros_jsonb ? 'criterion';

-- ============================================================
-- 5. Consultar registros que contienen un fragmento JSON
--
-- @> pregunta si el JSONB de la columna contiene el JSON indicado.
-- ============================================================

SELECT
    experimento_id,
    modelo_id,
    parametros_jsonb
FROM experimentos_modelos
WHERE parametros_jsonb @> '{"criterion": "gini"}'::jsonb;

-- ============================================================
-- 6. Crear índice GIN sobre JSONB
--
-- Los índices GIN son útiles para búsquedas de contención sobre JSONB,
-- especialmente con @> en tablas con muchos registros.
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_experimentos_modelos_parametros_jsonb
ON experimentos_modelos
USING GIN (parametros_jsonb);

-- Medir una consulta con @>.
EXPLAIN ANALYZE
SELECT
    experimento_id,
    modelo_id,
    parametros_jsonb
FROM experimentos_modelos
WHERE parametros_jsonb @> '{"criterion": "gini"}'::jsonb;

-- ============================================================
-- 7. Nota de diseño
--
-- JSONB suma flexibilidad cuando los atributos son variables entre
-- modelos o cuando cambian con frecuencia.
--
-- JSONB no reemplaza automáticamente el diseño relacional. Si un dato
-- es obligatorio, se consulta todo el tiempo, necesita claves foráneas
-- o participa en reglas de integridad fuertes, probablemente convenga
-- modelarlo como columna o tabla relacional.
-- ============================================================
