"""Pruebas unitarias para el módulo de exportación de reposición en Excel.

Verifica:
1. Cálculo de unidades sugeridas de reposición y stock de seguridad.
2. Generación estructurada de registros tabulares y ordenamiento por DCI ascendente.
3. Exportación física a archivo Excel (.xlsx) y validación de columnas obligatorias.
4. Manejo de listas vacías y casos sin alertas de desabastecimiento.
"""

import os
import tempfile
import pandas as pd
from openpyxl import load_workbook
import pytest

from src.data_ingestion import InventoryItem
from src.kpi_calculator import InventoryKPI
from src.alert_engine import Alert, AlertType, AlertSeverity
from src.replenishment_exporter import (
    calculate_suggested_replenishment,
    generate_replenishment_data,
    export_replenishment_excel,
)


def test_calculate_suggested_replenishment():
    """Valida la fórmula de cálculo de reposición."""
    calc = calculate_suggested_replenishment(
        stock_actual=4,
        venta_diaria=2.0,
        lead_time_dias=3,
        horizonte_dias=7,
        min_safety_stock=5,
    )
    # safety = max(5, ceil(2.0*3)) = 6
    # target = ceil(2.0*10) + 6 = 26
    # units = max(0, 26 - 4) = 22
    assert calc["stock_seguridad"] == 6
    assert calc["stock_objetivo"] == 26
    assert calc["unidades_reposicion"] == 22


def test_generate_replenishment_data_sorting():
    """Valida el ordenamiento por DCI ascendente en los datos de reposición."""
    item1 = InventoryItem(
        sku="CAMISA_OXFORD-S-AZUL",
        modelo="CAMISA_OXFORD",
        talla="S",
        color="AZUL",
        categoria="Hombre",
        tienda_id="T001",
        ciudad="Bogotá",
        stock_actual=10,
        ventas_ultimos_30d=30,
        precio_unitario=120000.0,
    )
    kpi1 = InventoryKPI(
        sku=item1.sku,
        tienda_id=item1.tienda_id,
        dci=10.0,
        venta_diaria_promedio=1.0,
        valor_inventario=1200000.0,
        estado_rotacion="ALERTA",
    )
    alert1 = Alert(
        alert_type=AlertType.WARNING_LOW_STOCK,
        severity=AlertSeverity.WARNING,
        sku=item1.sku,
        tienda_id=item1.tienda_id,
        mensaje="Bajo stock",
        dci=10.0,
        stock_actual=10,
    )

    item2 = InventoryItem(
        sku="JEAN_SLIM-32-INDIGO",
        modelo="JEAN_SLIM",
        talla="32",
        color="INDIGO",
        categoria="Hombre",
        tienda_id="T002",
        ciudad="Medellín",
        stock_actual=2,
        ventas_ultimos_30d=60,
        precio_unitario=180000.0,
    )
    kpi2 = InventoryKPI(
        sku=item2.sku,
        tienda_id=item2.tienda_id,
        dci=1.0,
        venta_diaria_promedio=2.0,
        valor_inventario=360000.0,
        estado_rotacion="QUIEBRE_INMINENTE",
    )
    alert2 = Alert(
        alert_type=AlertType.CRITICAL_STOCKOUT,
        severity=AlertSeverity.CRITICAL,
        sku=item2.sku,
        tienda_id=item2.tienda_id,
        mensaje="Quiebre crítico",
        dci=1.0,
        stock_actual=2,
    )

    records = generate_replenishment_data(
        items=[item1, item2],
        kpis=[kpi1, kpi2],
        alerts=[alert1, alert2],
    )

    assert len(records) == 2
    # El primer elemento debe ser el de menor DCI (JEAN_SLIM con DCI 1.0)
    assert records[0]["SKU"] == "JEAN_SLIM-32-INDIGO"
    assert records[0]["DCI_Dias_Cobertura"] == 1.0
    assert records[0]["Prioridad_Reposicion"] == "ALTA (URGENTE)"

    # El segundo elemento debe ser el de mayor DCI (CAMISA_OXFORD con DCI 10.0)
    assert records[1]["SKU"] == "CAMISA_OXFORD-S-AZUL"
    assert records[1]["Prioridad_Reposicion"] == "MEDIA (PREVENTIVA)"


def test_export_replenishment_excel_file():
    """Verifica la exportación física al archivo Excel y sus columnas."""
    item = InventoryItem(
        sku="VESTIDO_SEDA-M-ROJO",
        modelo="VESTIDO_SEDA",
        talla="M",
        color="ROJO",
        categoria="Mujer",
        tienda_id="T003",
        ciudad="Cali",
        stock_actual=1,
        ventas_ultimos_30d=30,
        precio_unitario=250000.0,
    )
    kpi = InventoryKPI(
        sku=item.sku,
        tienda_id=item.tienda_id,
        dci=1.0,
        venta_diaria_promedio=1.0,
        valor_inventario=250000.0,
        estado_rotacion="QUIEBRE_INMINENTE",
    )
    alert = Alert(
        alert_type=AlertType.CRITICAL_STOCKOUT,
        severity=AlertSeverity.CRITICAL,
        sku=item.sku,
        tienda_id=item.tienda_id,
        mensaje="Quiebre crítico",
        dci=1.0,
        stock_actual=1,
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        output_excel = os.path.join(tmpdir, "test_reposicion.xlsx")
        res = export_replenishment_excel(
            items=[item],
            kpis=[kpi],
            alerts=[alert],
            output_path=output_excel,
        )
        assert res == output_excel
        assert os.path.exists(output_excel)

        # Leer con pandas y validar columnas y pestañas
        df = pd.read_excel(output_excel, sheet_name="Orden_Reposicion_SKU")
        assert len(df) == 1
        assert "SKU" in df.columns
        assert "DCI_Dias_Cobertura" in df.columns
        assert "Unidades_Sugeridas_Reposicion" in df.columns
        assert "Inversion_Estimada_COP" in df.columns
        assert df.iloc[0]["SKU"] == "VESTIDO_SEDA-M-ROJO"

        wb = load_workbook(output_excel)
        assert "Orden_Reposicion_SKU" in wb.sheetnames
        assert "Resumen_Ejecutivo_Tiendas" in wb.sheetnames
        df_summary = pd.read_excel(output_excel, sheet_name="Resumen_Ejecutivo_Tiendas")
        assert len(df_summary) == 1
        assert df_summary.iloc[0]["Ciudad"] == "Cali"


def test_export_replenishment_empty():
    """Verifica que si no hay alertas de desabastecimiento, retorne None."""
    item = InventoryItem(
        sku="POLO_PIQUE-L-VERDE",
        modelo="POLO_PIQUE",
        talla="L",
        color="VERDE",
        categoria="Hombre",
        tienda_id="T001",
        ciudad="Bogotá",
        stock_actual=30,
        ventas_ultimos_30d=15,
        precio_unitario=90000.0,
    )
    kpi = InventoryKPI(
        sku=item.sku,
        tienda_id=item.tienda_id,
        dci=60.0,
        venta_diaria_promedio=0.5,
        valor_inventario=2700000.0,
        estado_rotacion="SOBRESTOCK",
    )
    alert = Alert(
        alert_type=AlertType.OVERSTOCK_RISK,
        severity=AlertSeverity.INFO,
        sku=item.sku,
        tienda_id=item.tienda_id,
        mensaje="Sobrestock",
        dci=60.0,
        stock_actual=30,
    )

    res = export_replenishment_excel(
        items=[item],
        kpis=[kpi],
        alerts=[alert],
        output_path="/tmp/should_not_exist.xlsx",
    )
    assert res is None
