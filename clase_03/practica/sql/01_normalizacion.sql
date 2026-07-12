-- ============================================================
-- Script 01
-- Ejercicio de normalización.
--
-- Clase 2 creó datasets.fuente y modelos.tipo como texto libre.
-- Ambas columnas repiten valores de categoría en varias filas. Eso
-- trae dos problemas típicos de un diseño sin normalizar:
-- - Si dos filas quieren decir lo mismo pero se escriben distinto
--   ("Clasificación" vs "clasificacion"), se pierde consistencia.
-- - Si la categoría necesitara datos propios (por ejemplo, una
--   descripción), habría que repetirlos en cada fila que la use.
--
-- Este script normaliza ambos casos siguiendo el mismo camino:
-- 1. Crear una tabla catálogo para la categoría.
-- 2. Agregar una columna de clave foránea y completarla según el
--    texto que ya existía.
-- 3. Eliminar la columna de texto libre original.
--
-- Pensado para ejecutarse una sola vez, después de Clase 2 y de
-- sql/00_poblar_datos_clase_03.sql.
-- ============================================================

-- ============================================================
-- 1. Normalizar datasets.fuente
--
-- fuente mezclaba dos ideas en un solo texto: una categoría general
-- ("IoT", "Sistema interno", "Aplicación"...) y un detalle más
-- específico ("IoT industrial", "Sistema transaccional"...).
-- Separamos la categoría en un catálogo (tipos_fuente) y dejamos el
-- detalle original en una columna de texto aparte (fuente_detalle).
-- ============================================================

CREATE TABLE IF NOT EXISTS tipos_fuente (
    id SERIAL PRIMARY KEY,
    nombre TEXT UNIQUE NOT NULL
);

INSERT INTO tipos_fuente(nombre)
VALUES
    ('IoT'),
    ('Sistema interno'),
    ('Aplicación'),
    ('Multimedia'),
    ('Servicio de soporte'),
    ('Servicio externo');

ALTER TABLE datasets
ADD COLUMN IF NOT EXISTS tipo_fuente_id INTEGER REFERENCES tipos_fuente(id);

ALTER TABLE datasets
ADD COLUMN IF NOT EXISTS fuente_detalle TEXT;

-- fuente_detalle conserva el texto original para no perder el
-- detalle específico de cada dataset.
UPDATE datasets
SET fuente_detalle = fuente;

-- tipo_fuente_id se completa según a qué categoría pertenece cada
-- valor de fuente. Esta clasificación es una decisión de diseño:
-- agrupa textos distintos que representan el mismo tipo de origen.
UPDATE datasets
SET tipo_fuente_id = (SELECT id FROM tipos_fuente WHERE nombre = 'IoT')
WHERE fuente IN ('IoT', 'IoT industrial');

UPDATE datasets
SET tipo_fuente_id = (SELECT id FROM tipos_fuente WHERE nombre = 'Sistema interno')
WHERE fuente IN ('Sistema transaccional', 'Sistema financiero');

UPDATE datasets
SET tipo_fuente_id = (SELECT id FROM tipos_fuente WHERE nombre = 'Aplicación')
WHERE fuente IN ('Aplicación web');

UPDATE datasets
SET tipo_fuente_id = (SELECT id FROM tipos_fuente WHERE nombre = 'Multimedia')
WHERE fuente IN ('Visión computacional');

UPDATE datasets
SET tipo_fuente_id = (SELECT id FROM tipos_fuente WHERE nombre = 'Servicio de soporte')
WHERE fuente IN ('Mesa de ayuda', 'Call center');

UPDATE datasets
SET tipo_fuente_id = (SELECT id FROM tipos_fuente WHERE nombre = 'Servicio externo')
WHERE fuente IN ('Servicio meteorológico');

-- Verificar que ningún dataset quedó sin categoría asignada.
-- Si esta consulta devuelve filas, hay un valor de fuente que no
-- fue contemplado en las clasificaciones anteriores.
SELECT id, nombre, fuente, tipo_fuente_id
FROM datasets
WHERE tipo_fuente_id IS NULL;

-- La columna original ya no hace falta: la categoría vive en
-- tipos_fuente y el detalle específico en fuente_detalle.
ALTER TABLE datasets DROP COLUMN IF EXISTS fuente;

-- Consultar el resultado normalizado.
SELECT
    d.id,
    d.nombre AS dataset,
    tf.nombre AS tipo_fuente,
    d.fuente_detalle
FROM datasets AS d
JOIN tipos_fuente AS tf
    ON tf.id = d.tipo_fuente_id
ORDER BY d.nombre;

-- ============================================================
-- 2. Normalizar modelos.tipo
--
-- tipo repite el mismo valor en varios modelos: "Clasificación"
-- aparece en varios registros distintos. Este es el caso más
-- directo de normalización: mover el valor repetido a una tabla
-- catálogo y referenciarlo por clave foránea.
-- ============================================================

CREATE TABLE IF NOT EXISTS tipos_modelo (
    id SERIAL PRIMARY KEY,
    nombre TEXT UNIQUE NOT NULL
);

-- A diferencia de tipos_fuente, acá no hace falta agrupar textos
-- distintos: cada valor de tipo ya es una categoría por sí sola.
INSERT INTO tipos_modelo(nombre)
SELECT DISTINCT tipo
FROM modelos
ORDER BY tipo;

ALTER TABLE modelos
ADD COLUMN IF NOT EXISTS tipo_modelo_id INTEGER REFERENCES tipos_modelo(id);

UPDATE modelos AS m
SET tipo_modelo_id = tm.id
FROM tipos_modelo AS tm
WHERE tm.nombre = m.tipo;

-- Verificar que ningún modelo quedó sin tipo asignado.
SELECT id, nombre, tipo, tipo_modelo_id
FROM modelos
WHERE tipo_modelo_id IS NULL;

ALTER TABLE modelos DROP COLUMN IF EXISTS tipo;

-- Consultar el resultado normalizado.
SELECT
    m.id,
    m.nombre AS modelo,
    tm.nombre AS tipo_modelo
FROM modelos AS m
JOIN tipos_modelo AS tm
    ON tm.id = m.tipo_modelo_id
ORDER BY tm.nombre, m.nombre;

-- ============================================================
-- 3. Qué cambió
--
-- Antes: datasets.fuente y modelos.tipo repetían texto libre en
-- cada fila, sin catálogo ni control de valores.
--
-- Ahora: tipos_fuente y tipos_modelo centralizan cada categoría en
-- una sola fila. Cambiar el nombre de una categoría se hace en un
-- solo lugar, y las columnas de clave foránea (tipo_fuente_id,
-- tipo_modelo_id) evitan valores inconsistentes.
--
-- Esto aplica el mismo criterio de 3FN visto en la teórica: la
-- categoría ya no depende de un texto libre en cada fila, sino de
-- una clave foránea hacia su propia tabla.
-- ============================================================
