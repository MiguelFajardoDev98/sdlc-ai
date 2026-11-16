#!/usr/bin/env bash
set -e

echo "================================================================================"
echo "  SDLC-AI: Framework de Inteligencia Artificial Agéntica para el SDLC"
echo "  Orquestador Multi-Proyecto y Verificación de Quality Gates"
echo "================================================================================"
echo ""

TARGET="${1:-all}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

run_harness() {
    echo "[PASO 1] Verificando contratos de gobernanza y habilidades del arnés agéntico..."
    pytest tests/
    echo "  ✔ Arnés operativo y contratos de agentes certificados."
    echo ""
}

run_docx() {
    echo "[PASO 2] Verificando Subproyecto 1: docx_to_markdown (Herramienta CLI)..."
    (cd docx_to_markdown && ./run.sh)
    echo ""
}

run_retail() {
    echo "[PASO 3] Verificando Caso de Estudio 1: case_studies/retail_inventory/..."
    (cd case_studies/retail_inventory && ./run.sh)
    echo ""
}

run_todo() {
    echo "[PASO 4] Verificando Caso de Estudio 2: case_studies/todo_list/ y Benchmark A/B..."
    (cd case_studies/todo_list && ./run.sh)
    python3 benchmarks/todo_list/blind_chaos_suite.py
    echo ""
}

case "$TARGET" in
    harness)
        run_harness
        ;;
    docx)
        run_docx
        ;;
    retail)
        run_retail
        ;;
    todo|benchmark)
        run_todo
        ;;
    all)
        run_harness
        run_docx
        run_retail
        run_todo
        echo "================================================================================"
        echo "  TODOS LOS PROYECTOS, CASOS DE ESTUDIO Y BENCHMARKS SUPERARON SUS GATES"
        echo "================================================================================"
        ;;
    *)
        echo "Uso: ./run.sh [all|harness|docx|retail|todo]"
        exit 1
        ;;
esac
