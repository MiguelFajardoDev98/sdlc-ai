#!/usr/bin/env bash
set -e

echo "================================================================================"
echo "  SDLC-AI — Caso de Estudio: Sistema Analítico y Reposición para Retail"
echo "  Ruta del Caso de Estudio: case_studies/retail_inventory/"
echo "================================================================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export PYTHONPATH=.

echo "[PASO 1/3] Ejecutando suite de pruebas unitarias y cobertura (Quality Gate: >= 80%)..."
python3 -m pytest tests/ --cov=src --cov-report=term-missing

echo ""
echo "[PASO 2/3] Ejecutando análisis estático con Pylint (Quality Gate: >= 7.0/10.0)..."
python3 -m pylint src/

echo ""
echo "[PASO 3/3] Ejecutando Pipeline E2E (Ingesta -> KPIs -> Alertas -> Gemini Pro -> Excel)..."
python3 src/main.py

echo ""
echo "================================================================================"
echo "  CASO DE ESTUDIO COMPLETADO EXITOSAMENTE"
echo "  - Reporte Ejecutivo: logs/executive_report.md"
echo "  - Reporte Excel: logs/reporte_reposicion_inventario.xlsx"
echo "  - Métricas de Telemetría: logs/execution_metrics.json"
echo "================================================================================"
