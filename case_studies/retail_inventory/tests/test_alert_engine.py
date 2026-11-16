"""Pruebas unitarias y de validación analítica del motor de alertas."""

import csv
import pytest
from src.alert_engine import AlertEngine, AlertSeverity, AlertType
from src.data_ingestion import InventoryItem, load_inventory_csv


def test_alert_engine_critical_stockout():
    """Verifica emisión de alerta crítica ante quiebre o DCI < 7."""
    engine = AlertEngine()
    item = InventoryItem(
        sku="CAMISA_OXFORD-M-AZUL",
        modelo="CAMISA_OXFORD",
        talla="M",
        color="AZUL",
        categoria="Hombre",
        tienda_id="T001",
        ciudad="Bogotá",
        stock_actual=2,
        ventas_ultimos_30d=30,  # 1 u/d -> DCI = 2 días < 7
        precio_unitario=120000.0,
    )
    alert = engine.evaluate_item(item)
    assert alert.alert_type == AlertType.CRITICAL_STOCKOUT
    assert alert.severity == AlertSeverity.CRITICAL


def test_alert_engine_warning_low_stock():
    """Verifica alerta de advertencia ante 7 <= DCI < 15."""
    engine = AlertEngine()
    item = InventoryItem(
        sku="POLO_PIQUE-S-NEGRO",
        modelo="POLO_PIQUE",
        talla="S",
        color="NEGRO",
        categoria="Hombre",
        tienda_id="T002",
        ciudad="Medellín",
        stock_actual=10,
        ventas_ultimos_30d=30,  # DCI = 10 días
        precio_unitario=85000.0,
    )
    alert = engine.evaluate_item(item)
    assert alert.alert_type == AlertType.WARNING_LOW_STOCK
    assert alert.severity == AlertSeverity.WARNING


def test_alert_engine_overstock():
    """Verifica alerta de sobrestock ante DCI > 45."""
    engine = AlertEngine()
    item = InventoryItem(
        sku="VESTIDO_SEDA-L-ROJO",
        modelo="VESTIDO_SEDA",
        talla="L",
        color="ROJO",
        categoria="Mujer",
        tienda_id="T003",
        ciudad="Cali",
        stock_actual=60,
        ventas_ultimos_30d=30,  # DCI = 60 días > 45
        precio_unitario=180000.0,
    )
    alert = engine.evaluate_item(item)
    assert alert.alert_type == AlertType.OVERSTOCK_RISK


def test_alert_engine_transfers():
    """Verifica detección de oportunidades de transferencia intertienda."""
    engine = AlertEngine()
    items = [
        # Tienda 1 con sobrestock (stock 50, ventas 10 -> DCI 150)
        InventoryItem("JEAN_SLIM-32-AZUL", "JEAN_SLIM", "32", "AZUL", "Hombre", "T001", "Bogotá", 50, 10, 140000.0),
        # Tienda 2 en quiebre (stock 1, ventas 30 -> DCI 1)
        InventoryItem("JEAN_SLIM-32-AZUL", "JEAN_SLIM", "32", "AZUL", "Hombre", "T002", "Medellín", 1, 30, 140000.0),
    ]
    transfers = engine.detect_transfers(items)
    assert len(transfers) >= 1
    t = transfers[0]
    assert t.alert_type == AlertType.TRANSFER_OPPORTUNITY
    assert t.sku == "JEAN_SLIM-32-AZUL"
    assert t.tienda_id == "T001"
    assert t.tienda_destino == "T002"
    assert t.unidades_sugeridas == 10


def test_alert_engine_f1_score_validation():
    """Evalúa el macro F1-score contra el dataset sintético de 450 registros."""
    engine = AlertEngine()
    items = load_inventory_csv("data/synthetic_retail_data.csv")

    with open("data/synthetic_retail_data.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        ground_truth = [r["ground_truth_alert"] for r in reader]

    metrics = engine.compute_metrics(items, ground_truth)
    assert "macro_f1" in metrics
    # Quality Gate obligatorio: F1-score >= 0.80
    assert metrics["macro_f1"] >= 0.80, f"F1-score insuficiente: {metrics['macro_f1']}"
