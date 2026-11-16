"""Módulo de Exportación y Generación de Órdenes de Reposición en Excel.

Este módulo toma los ítems evaluados, sus KPIs logísticos y las alertas generadas
por AlertEngine, filtra las referencias en riesgo inminente de quiebre o bajo stock,
calcula las unidades necesarias de reabastecimiento en función de la velocidad de venta,
el tiempo de reposición (lead time) y el stock de seguridad, y genera un reporte operativo
en formato Excel (.xlsx) con semaforización visual y resumen ejecutivo por ciudad.
"""

import math
import os
from typing import Dict, List, Optional
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

try:
    from src.data_ingestion import InventoryItem
    from src.kpi_calculator import InventoryKPI
    from src.alert_engine import Alert, AlertType
except ImportError:
    from data_ingestion import InventoryItem  # type: ignore
    from kpi_calculator import InventoryKPI  # type: ignore
    from alert_engine import Alert, AlertType  # type: ignore

LEAD_TIME_BY_CITY: Dict[str, int] = {
    "Bogotá": 3,
    "Medellín": 4,
    "Cali": 5,
    "Barranquilla": 6,
    "Bucaramanga": 5,
}

_HEADER_FILL = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
_HEADER_FONT = Font(color="FFFFFF", bold=True, size=10)
_CRITICAL_FILL = PatternFill(start_color="FADBD8", end_color="FADBD8", fill_type="solid")
_CRITICAL_FONT = Font(color="922B21", bold=True, size=10)
_WARNING_FILL = PatternFill(start_color="FCF3CF", end_color="FCF3CF", fill_type="solid")
_WARNING_FONT = Font(color="7D6608", bold=True, size=10)
_COP_FORMAT = "$#,##0"


def calculate_suggested_replenishment(
    stock_actual: int,
    venta_diaria: float,
    lead_time_dias: int,
    horizonte_dias: int = 7,
    min_safety_stock: int = 5,
) -> Dict[str, int]:
    """Calcula el stock de seguridad y las unidades sugeridas de reposición.

    Args:
        stock_actual: Unidades físicas actualmente en tienda.
        venta_diaria: Promedio diario de unidades vendidas.
        lead_time_dias: Tiempo de entrega estimado del proveedor/CEDI en días.
        horizonte_dias: Días de cobertura comercial objetivo adicional (default: 7).
        min_safety_stock: Unidades mínimas de reserva (default: 5).

    Returns:
        Diccionario con 'stock_seguridad', 'stock_objetivo' y 'unidades_reposicion'.
    """
    safety_stock = max(min_safety_stock, int(math.ceil(venta_diaria * 3.0)))
    dias_totales = lead_time_dias + horizonte_dias
    target_stock = int(math.ceil(venta_diaria * dias_totales)) + safety_stock
    units_to_order = max(0, target_stock - stock_actual)
    return {
        "stock_seguridad": safety_stock,
        "stock_objetivo": target_stock,
        "unidades_reposicion": units_to_order,
    }


def generate_replenishment_data(
    items: List[InventoryItem],
    kpis: List[InventoryKPI],
    alerts: List[Alert],
    default_lead_time_days: int = 5,
) -> List[Dict[str, object]]:
    """Genera la estructura de datos tabulares de productos a reponer.

    Args:
        items: Lista de InventoryItem evaluados.
        kpis: Lista de InventoryKPI correspondientes a cada ítem.
        alerts: Lista de Alert generadas para cada ítem.
        default_lead_time_days: Días de reposición por defecto si la ciudad no está mapeada.

    Returns:
        Lista de diccionarios con la información detallada para el Excel.
    """
    records: List[Dict[str, object]] = []

    for item, kpi, alert in zip(items, kpis, alerts):
        if alert.alert_type not in (
            AlertType.CRITICAL_STOCKOUT,
            AlertType.WARNING_LOW_STOCK,
        ):
            continue

        lead_time = LEAD_TIME_BY_CITY.get(item.ciudad, default_lead_time_days)
        calc = calculate_suggested_replenishment(
            stock_actual=item.stock_actual,
            venta_diaria=kpi.venta_diaria_promedio,
            lead_time_dias=lead_time,
        )

        is_critical = alert.alert_type == AlertType.CRITICAL_STOCKOUT
        costo_estimado = round(item.precio_unitario * 0.45, 2)
        inversion_estimada = round(calc["unidades_reposicion"] * costo_estimado, 2)

        records.append(
            {
                "SKU": item.sku,
                "Modelo": item.modelo,
                "Talla": item.talla,
                "Color": item.color,
                "Categoría": item.categoria,
                "Tienda_ID": item.tienda_id,
                "Ciudad": item.ciudad,
                "Stock_Actual": item.stock_actual,
                "Ventas_30d": item.ventas_ultimos_30d,
                "Venta_Diaria_Promedio": round(kpi.venta_diaria_promedio, 2),
                "DCI_Dias_Cobertura": kpi.dci,
                "Estado_Alerta": "QUIEBRE CRÍTICO" if is_critical else "BAJO STOCK",
                "Prioridad_Reposicion": "ALTA (URGENTE)" if is_critical else "MEDIA (PREVENTIVA)",
                "Lead_Time_Dias": lead_time,
                "Stock_Seguridad": calc["stock_seguridad"],
                "Unidades_Sugeridas_Reposicion": calc["unidades_reposicion"],
                "Costo_Unitario_COP": costo_estimado,
                "Inversion_Estimada_COP": inversion_estimada,
            }
        )

    records.sort(
        key=lambda r: (
            float(str(r["DCI_Dias_Cobertura"])),
            -float(str(r["Venta_Diaria_Promedio"])),
        )
    )
    return records


def _style_worksheet(
    worksheet: Worksheet,
    currency_headers: tuple[str, ...],
    alert_headers: tuple[str, ...] = (),
) -> None:
    """Aplica encabezados corporativos, semaforización y ajuste de columnas a una hoja."""
    headers = [str(cell.value) for cell in worksheet[1]]
    for cell in worksheet[1]:
        cell.fill = _HEADER_FILL
        cell.font = _HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center")

    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions

    for row in worksheet.iter_rows(min_row=2, max_row=worksheet.max_row):
        for cell, header in zip(row, headers):
            if header in currency_headers:
                cell.number_format = _COP_FORMAT
            if header in alert_headers:
                val = str(cell.value)
                if "CRÍTICO" in val or "ALTA" in val:
                    cell.fill = _CRITICAL_FILL
                    cell.font = _CRITICAL_FONT
                elif "BAJO" in val or "MEDIA" in val:
                    cell.fill = _WARNING_FILL
                    cell.font = _WARNING_FONT

    for idx, col_cells in enumerate(worksheet.columns, start=1):
        max_len = max(len(str(c.value or "")) for c in col_cells)
        worksheet.column_dimensions[get_column_letter(idx)].width = min(max_len + 4, 36)


def export_replenishment_excel(
    items: List[InventoryItem],
    kpis: List[InventoryKPI],
    alerts: List[Alert],
    output_path: str = "logs/reporte_reposicion_inventario.xlsx",
    default_lead_time_days: int = 5,
) -> Optional[str]:
    """Exporta las necesidades de reposición a un libro de Excel (.xlsx) con dos hojas.

    Args:
        items: Lista de InventoryItem.
        kpis: Lista de InventoryKPI.
        alerts: Lista de Alert.
        output_path: Ruta destino del archivo Excel.
        default_lead_time_days: Días de reposición por defecto.

    Returns:
        Ruta del archivo generado si hubo registros, o None si no hubo alertas de reposición.
    """
    records = generate_replenishment_data(
        items=items,
        kpis=kpis,
        alerts=alerts,
        default_lead_time_days=default_lead_time_days,
    )

    if not records:
        return None

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    df_detail = pd.DataFrame(records)
    df_summary = (
        df_detail.groupby(["Ciudad", "Tienda_ID"], as_index=False)
        .agg(
            SKUs_en_Riesgo=("SKU", "count"),
            Unidades_Totales_Reponer=("Unidades_Sugeridas_Reposicion", "sum"),
            Inversion_Total_COP=("Inversion_Estimada_COP", "sum"),
        )
        .sort_values(by="Inversion_Total_COP", ascending=False)
    )

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df_detail.to_excel(writer, sheet_name="Orden_Reposicion_SKU", index=False)
        df_summary.to_excel(writer, sheet_name="Resumen_Ejecutivo_Tiendas", index=False)

    workbook = load_workbook(output_path)
    _style_worksheet(
        workbook["Orden_Reposicion_SKU"],
        currency_headers=("Costo_Unitario_COP", "Inversion_Estimada_COP"),
        alert_headers=("Estado_Alerta", "Prioridad_Reposicion"),
    )
    _style_worksheet(
        workbook["Resumen_Ejecutivo_Tiendas"],
        currency_headers=("Inversion_Total_COP",),
    )
    workbook.save(output_path)
    return output_path
