"""Pruebas unitarias para el módulo de cálculo de KPIs logísticos."""

from src.data_ingestion import InventoryItem
from src.kpi_calculator import calculate_item_kpi, calculate_store_kpis


def test_calculate_item_kpi_optimo():
    """Verifica el cálculo de DCI dentro de rango óptimo."""
    item = InventoryItem(
        sku="CAMISA_OXFORD-M-AZUL",
        modelo="CAMISA_OXFORD",
        talla="M",
        color="AZUL",
        categoria="Hombre",
        tienda_id="T001",
        ciudad="Bogotá",
        stock_actual=30,
        ventas_ultimos_30d=30,  # 1 unidad/día -> DCI = 30 días
        precio_unitario=100000.0,
    )
    kpi = calculate_item_kpi(item)
    assert kpi.dci == 30.0
    assert kpi.venta_diaria_promedio == 1.0
    assert kpi.valor_inventario == 3000000.0
    assert kpi.estado_rotacion == "OPTIMO"


def test_calculate_item_kpi_quiebre():
    """Verifica la detección de quiebre de stock con demanda activa."""
    item = InventoryItem(
        sku="POLO_PIQUE-S-NEGRO",
        modelo="POLO_PIQUE",
        talla="S",
        color="NEGRO",
        categoria="Hombre",
        tienda_id="T002",
        ciudad="Medellín",
        stock_actual=0,
        ventas_ultimos_30d=45,
        precio_unitario=80000.0,
    )
    kpi = calculate_item_kpi(item)
    assert kpi.dci == 0.0
    assert kpi.estado_rotacion == "QUIEBRE"


def test_calculate_item_kpi_zero_ventas_positive_stock():
    """Verifica que sin ventas pero con stock se asigne DCI = 999.0 (sobrestock)."""
    item = InventoryItem(
        sku="VESTIDO_SEDA-L-ROJO",
        modelo="VESTIDO_SEDA",
        talla="L",
        color="ROJO",
        categoria="Mujer",
        tienda_id="T003",
        ciudad="Cali",
        stock_actual=15,
        ventas_ultimos_30d=0,
        precio_unitario=200000.0,
    )
    kpi = calculate_item_kpi(item)
    assert kpi.dci == 999.0
    assert kpi.estado_rotacion == "SOBRESTOCK"


def test_calculate_store_kpis_aggregate():
    """Verifica las métricas consolidadas de tienda (TQS y valor total)."""
    items = [
        InventoryItem("M1-S-A", "M1", "S", "A", "C", "T1", "BOG", 10, 10, 50000.0),
        InventoryItem("M2-M-B", "M2", "M", "B", "C", "T1", "BOG", 0, 15, 60000.0),  # Quiebre
    ]
    summary = calculate_store_kpis(items)
    assert summary["total_skus"] == 2
    assert summary["total_unidades"] == 10
    assert summary["valor_total_inventario"] == 500000.0
    assert summary["skus_en_quiebre"] == 1
    assert summary["tasa_quiebre_stock_pct"] == 50.0


def test_calculate_store_kpis_empty():
    """Verifica el comportamiento con lista vacía."""
    summary = calculate_store_kpis([])
    assert summary["total_skus"] == 0
    assert summary["tasa_quiebre_stock_pct"] == 0.0
