#!/usr/bin/env bash
# Script de ejecución y verificación autónoma de docx_to_markdown

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}/src"

echo "=========================================================="
echo "DOCX to Markdown Converter — Verificación de Quality Gates"
echo "=========================================================="

echo "[1/3] Ejecutando análisis estático con Pylint..."
pylint "${SCRIPT_DIR}/src/docx_to_markdown" "${SCRIPT_DIR}/tests"

echo "[2/3] Ejecutando suite de pruebas unitarias y cobertura con Pytest..."
pytest "${SCRIPT_DIR}/tests" --cov="${SCRIPT_DIR}/src/docx_to_markdown" --cov-report=term-missing

echo "[3/3] Prueba funcional E2E con documento real..."
if [[ -f "${SCRIPT_DIR}/../docs/SDLC-AI_Tesis_Entrega1.docx" ]]; then
    python -m docx_to_markdown.cli \
        --input "${SCRIPT_DIR}/../docs/SDLC-AI_Tesis_Entrega1.docx" \
        --output "${SCRIPT_DIR}/docs/SDLC-AI_Tesis_Entrega1_convertida.md"
    echo "✔ Conversión E2E de tesis verificada exitosamente."
fi

echo "=========================================================="
echo "✔ Todos los Quality Gates superados exitosamente."
echo "=========================================================="
