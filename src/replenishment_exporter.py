"""Módulo de Exportación y Generación de Órdenes de Reposición en Excel.

Este módulo toma los ítems evaluados, sus KPIs logísticos y las alertas generadas
por AlertEngine, filtra las referencias en riesgo inminente de quiebre o bajo stock,
calcula las unidades necesarias de reabastecimiento en función de la velocidad de venta,
el tiempo de reposición (lead time) y el stock de seguridad, y genera un reporte operativo
en formato Excel (.xlsx) priorizado para el equipo de compras y logística.
"""

import math
import os
from typing import Dict, List, Optional
import pandas as pd

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

        prioridad = (
            "ALTA (URGENTE)"
            if alert.alert_type == AlertType.CRITICAL_STOCKOUT
            else "MEDIA (PREVENTIVA)"
        )
        estado_alerta = (
            "QUIEBRE CRÍTICO"
            if alert.alert_type == AlertType.CRITICAL_STOCKOUT
            else "BAJO STOCK"
        )

        # Costo unitario estimado como 45% del PVP textil en Colombia
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
                "Estado_Alerta": estado_alerta,
                "Prioridad_Reposicion": prioridad,
                "Lead_Time_Dias": lead_time,
                "Stock_Seguridad": calc["stock_seguridad"],
                "Unidades_Sugeridas_Reposicion": calc["unidades_reposicion"],
                "Costo_Unitario_COP": costo_estimado,
                "Inversion_Estimada_COP": inversion_estimada,
            }
        )

    # Ordenar prioritariamente por DCI ascendente (los más próximos a agotarse primero)
    records.sort(
        key=lambda r: (
            float(str(r["DCI_Dias_Cobertura"])),
            -float(str(r["Venta_Diaria_Promedio"])),
        )
    )
    return records


def export_replenishment_excel(
    items: List[InventoryItem],
    kpis: List[InventoryKPI],
    alerts: List[Alert],
    output_path: str = "logs/reporte_reposicion_inventario.xlsx",
    default_lead_time_days: int = 5,
) -> Optional[str]:
    """Exporta las necesidades de reposición a un libro de Excel (.xlsx).

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

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df = pd.DataFrame(records)
    df.to_excel(output_path, index=False, engine="openpyxl")
    return output_path
