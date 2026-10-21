#!/usr/bin/env bash
set -e

echo "================================================================================"
echo "  SDLC-AI: Framework de Inteligencia Artificial Agéntica para el SDLC"
echo "  Caso de Estudio: Alertas de Inventario para Retail de Moda en Colombia"
echo "  Convención de SKU: MODELO-TALLA-COLOR"
echo "================================================================================"
echo ""

export PYTHONPATH=.

echo "[PASO 1/3] Ejecutando suite de pruebas unitarias y cobertura (Quality Gate: >= 80%)..."
python3 -m pytest tests/ --cov=src --cov-report=term-missing

echo ""
echo "[PASO 2/3] Ejecutando análisis estático con Pylint (Quality Gate: >= 7.0/10.0)..."
python3 -m pylint src/

echo ""
echo "[PASO 3/3] Ejecutando Pipeline E2E (Ingesta -> KPIs -> Alertas -> Gemini Pro)..."
python3 src/main.py

echo ""
echo "================================================================================"
echo "  EJECUCIÓN DEL PIPELINE SDLC-AI COMPLETADA CON ÉXITO"
echo "  - Reporte Ejecutivo: logs/executive_report.md"
echo "  - Métricas de Telemetría: logs/execution_metrics.json"
echo "================================================================================"
