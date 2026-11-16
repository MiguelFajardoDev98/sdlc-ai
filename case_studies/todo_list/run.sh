#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export PYTHONPATH="$SCRIPT_DIR/src"
PORT="${TODO_PORT:-8082}"
HOST="${TODO_HOST:-127.0.0.1}"

if [[ "${1:-}" == "serve" || "${1:-}" == "--serve" ]]; then
    echo "Iniciando servidor Web To-Do List en http://${HOST}:${PORT} ..."
    exec python3 -m todo_list.web --host "$HOST" --port "$PORT"
fi

echo "================================================================================"
echo "  SDLC-AI — Caso de Estudio: Aplicación de Lista de Tareas (To-Do List)"
echo "  Ruta del Caso de Estudio: case_studies/todo_list/"
echo "================================================================================"
echo ""

echo "[PASO 1/3] Ejecutando suite de pruebas unitarias y cobertura (Quality Gate: >= 85%)..."
python3 -m pytest tests/ --cov=src/todo_list --cov-report=term-missing

echo ""
echo "[PASO 2/3] Ejecutando análisis estático con Pylint (Quality Gate: 10.00/10)..."
if [[ -f "/home/admin/Projects/Academico/2026-02/TrabajoDeGrado/SDLC-AI/.pylintrc" ]]; then
    python3 -m pylint --rcfile="/home/admin/Projects/Academico/2026-02/TrabajoDeGrado/SDLC-AI/.pylintrc" src/todo_list/ tests/
else
    python3 -m pylint src/todo_list/ tests/
fi

echo ""
echo "[PASO 3/3] Verificando inicialización de aplicación WSGI y persistencia JSON (Puerto ${PORT})..."
python3 -m todo_list.web --check --port "$PORT"

echo ""
echo "================================================================================"
echo "  CASO DE ESTUDIO TODO_LIST CERTIFICADO EXITOSAMENTE"
echo "  - Para iniciar el servidor Web interactivo ejecute: ./run.sh serve"
echo "  - URL por defecto: http://${HOST}:${PORT}"
echo "  - Reporte QA: logs/qa_report.json"
echo "================================================================================"
