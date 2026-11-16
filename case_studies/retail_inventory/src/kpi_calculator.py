"""Módulo de Cálculo de KPIs Logísticos de Inventario.

Este módulo implementa el cómputo de indicadores clave de rendimiento (KPIs)
para el retail de moda textil en Colombia: Días de Cobertura de Inventario (DCI),
Tasa de Quiebre de Stock (TQS) y valorización de inventario.
"""

from dataclasses import dataclass
from typing import Dict, List, Any

try:
    from src.data_ingestion import InventoryItem
except ImportError:
    from data_ingestion import InventoryItem  # type: ignore


@dataclass
class InventoryKPI:
    """Contenedor de métricas calculadas para un SKU en una tienda específica."""

    sku: str
    tienda_id: str
    dci: float
    venta_diaria_promedio: float
    valor_inventario: float
    estado_rotacion: str


def calculate_item_kpi(item: InventoryItem) -> InventoryKPI:
    """Calcula los indicadores logísticos para un ítem de inventario.

    Args:
        item: Objeto InventoryItem con información de stock y ventas.

    Returns:
        Objeto InventoryKPI con DCI, venta diaria y estado de rotación.
    """
    venta_diaria = item.ventas_ultimos_30d / 30.0
    valor_inventario = item.stock_actual * item.precio_unitario

    if venta_diaria > 0:
        dci = round(item.stock_actual / venta_diaria, 2)
    else:
        # Si no hay ventas pero hay stock, la cobertura es virtualmente infinita (sin rotación)
        dci = 999.0 if item.stock_actual > 0 else 0.0

    if dci == 0.0 or (item.stock_actual == 0 and venta_diaria > 0):
        estado = "QUIEBRE"
    elif dci < 7.0:
        estado = "QUIEBRE_INMINENTE"
    elif dci < 15.0:
        estado = "BAJA_COBERTURA"
    elif dci <= 45.0:
        estado = "OPTIMO"
    else:
        estado = "SOBRESTOCK"

    return InventoryKPI(
        sku=item.sku,
        tienda_id=item.tienda_id,
        dci=dci,
        venta_diaria_promedio=round(venta_diaria, 2),
        valor_inventario=round(valor_inventario, 2),
        estado_rotacion=estado,
    )


def calculate_store_kpis(items: List[InventoryItem]) -> Dict[str, Any]:
    """Calcula métricas logísticas agregadas para un conjunto de ítems de tienda.

    Args:
        items: Lista de InventoryItem.

    Returns:
        Diccionario con indicadores agregados (TQS, valor total, unidades).
    """
    if not items:
        return {
            "total_skus": 0,
            "total_unidades": 0,
            "valor_total_inventario": 0.0,
            "tasa_quiebre_stock_pct": 0.0,
            "skus_en_quiebre": 0,
        }

    total_skus = len(items)
    total_unidades = sum(item.stock_actual for item in items)
    valor_total = sum(item.stock_actual * item.precio_unitario for item in items)
    skus_en_quiebre = sum(1 for item in items if item.stock_actual == 0)

    tqs = round((skus_en_quiebre / total_skus) * 100.0, 2)

    return {
        "total_skus": total_skus,
        "total_unidades": total_unidades,
        "valor_total_inventario": round(valor_total, 2),
        "tasa_quiebre_stock_pct": tqs,
        "skus_en_quiebre": skus_en_quiebre,
    }
