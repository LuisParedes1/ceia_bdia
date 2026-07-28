#!/bin/sh
# Objetivo: devolver exclusivamente la práctica de Clase 5 a un estado inicial vacío.
# Requiere / entradas: ejecutar desde clase_05/practica, donde Compose resuelve su proyecto.
# Produce / modifica: elimina contenedores, red y volúmenes del proyecto bdia_clase_05.
# Resultado esperado: próxima ejecución recrea infraestructura, Bronze, DuckDB y Warehouse.
# Guía: recuperación determinista ante carga parcial; no es un paso normal de enseñanza.
# Seguridad: DESTRUCTIVO; pierde todo estado persistido de esta práctica, no datos fuente.
set -eu

# El directorio de trabajo define qué archivo y nombre de proyecto Compose administra.
docker compose down -v --remove-orphans
echo "Se eliminaron únicamente contenedores, red y volúmenes del proyecto bdia_clase_05."
