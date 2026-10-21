"""Motor Analítico de Alertas Tempranas de Inventario para Retail de Moda.

Este módulo evalúa los indicadores logísticos de inventario por SKU y tienda,
generando alertas de quiebre crítico, baja cobertura, sobrestock y recomendaciones
de redistribución y transferencia multitienda.
"""

from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

try:
    from src.data_ingestion import InventoryItem
    from src.kpi_calculator import InventoryKPI, calculate_item_kpi
except ImportError:
    from data_ingestion import InventoryItem  # type: ignore
    from kpi_calculator import InventoryKPI, calculate_item_kpi  # type: ignore


class AlertSeverity(str, Enum):
    """Niveles de severidad operativa de una alerta."""

    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"
    OPPORTUNITY = "OPPORTUNITY"


class AlertType(str, Enum):
    """Tipos funcionales de alertas de inventario."""

    CRITICAL_STOCKOUT = "CRITICAL_STOCKOUT"
    WARNING_LOW_STOCK = "WARNING_LOW_STOCK"
    OVERSTOCK_RISK = "OVERSTOCK_RISK"
    HEALTHY = "HEALTHY"
    TRANSFER_OPPORTUNITY = "TRANSFER_OPPORTUNITY"


@dataclass
class Alert:  # pylint: disable=too-many-instance-attributes
    """Representa una alerta analítica generada por el motor."""

    alert_type: AlertType
    severity: AlertSeverity
    sku: str
    tienda_id: str
    mensaje: str
    dci: float
    stock_actual: int
    tienda_destino: Optional[str] = None
    unidades_sugeridas: Optional[int] = None


class AlertEngine:
    """Motor de evaluación de reglas de inventario y generación de alertas."""

    def __init__(
        self,
        critical_dci_threshold: float = 7.0,
        warning_dci_threshold: float = 15.0,
        overstock_dci_threshold: float = 45.0,
        min_transfer_safety_stock: int = 5,
    ) -> None:
        """Inicializa los umbrales configurables del motor."""
        self.critical_dci = critical_dci_threshold
        self.warning_dci = warning_dci_threshold
        self.overstock_dci = overstock_dci_threshold
        self.min_safety_stock = min_transfer_safety_stock

    def evaluate_item(self, item: InventoryItem, kpi: Optional[InventoryKPI] = None) -> Alert:
        """Evalúa un ítem de inventario y genera su alerta correspondiente.

        Args:
            item: Objeto InventoryItem.
            kpi: Objeto InventoryKPI precalculado (opcional).

        Returns:
            Instancia de Alert con la clasificación de riesgo.
        """
        if kpi is None:
            kpi = calculate_item_kpi(item)

        dci = kpi.dci

        if dci < self.critical_dci or (item.stock_actual == 0 and item.ventas_ultimos_30d > 0):
            msg = (
                f"Quiebre crítico en SKU {item.sku}. DCI: {dci} días. "
                f"Stock actual: {item.stock_actual}"
            )
            return Alert(
                alert_type=AlertType.CRITICAL_STOCKOUT,
                severity=AlertSeverity.CRITICAL,
                sku=item.sku,
                tienda_id=item.tienda_id,
                mensaje=msg,
                dci=dci,
                stock_actual=item.stock_actual,
            )

        if dci < self.warning_dci:
            return Alert(
                alert_type=AlertType.WARNING_LOW_STOCK,
                severity=AlertSeverity.WARNING,
                sku=item.sku,
                tienda_id=item.tienda_id,
                mensaje=f"Bajo stock en SKU {item.sku}. DCI: {dci} días. Se recomienda reposición.",
                dci=dci,
                stock_actual=item.stock_actual,
            )

        if dci > self.overstock_dci or (item.stock_actual > 20 and item.ventas_ultimos_30d <= 2):
            return Alert(
                alert_type=AlertType.OVERSTOCK_RISK,
                severity=AlertSeverity.INFO,
                sku=item.sku,
                tienda_id=item.tienda_id,
                mensaje=f"Riesgo de sobrestock en SKU {item.sku}. DCI: {dci} días.",
                dci=dci,
                stock_actual=item.stock_actual,
            )

        return Alert(
            alert_type=AlertType.HEALTHY,
            severity=AlertSeverity.INFO,
            sku=item.sku,
            tienda_id=item.tienda_id,
            mensaje=f"Stock equilibrado en SKU {item.sku}. DCI: {dci} días.",
            dci=dci,
            stock_actual=item.stock_actual,
        )

    def evaluate_inventory(self, items: List[InventoryItem]) -> List[Alert]:
        """Evalúa un lote completo de inventario y retorna todas las alertas.

        Args:
            items: Lista de InventoryItem.

        Returns:
            Lista de alertas emitidas.
        """
        return [self.evaluate_item(item) for item in items]

    def detect_transfers(self, items: List[InventoryItem]) -> List[Alert]:
        """Identifica oportunidades de redistribución de mercancía entre tiendas.

        Args:
            items: Lista de InventoryItem de múltiples tiendas.

        Returns:
            Lista de alertas tipo TRANSFER_OPPORTUNITY.
        """
        transfers: List[Alert] = []
        sku_groups: Dict[str, List[InventoryItem]] = defaultdict(list)

        for item in items:
            sku_groups[item.sku].append(item)

        for sku, store_items in sku_groups.items():
            overstocked = [
                i for i in store_items if calculate_item_kpi(i).dci > self.overstock_dci
            ]
            depleted = [
                i for i in store_items if calculate_item_kpi(i).dci < self.critical_dci
            ]

            for origin in overstocked:
                available_to_send = origin.stock_actual - self.min_safety_stock
                if available_to_send <= 0:
                    continue

                for destination in depleted:
                    suggested_qty = min(available_to_send, 10)
                    if suggested_qty <= 0:
                        continue

                    alert = Alert(
                        alert_type=AlertType.TRANSFER_OPPORTUNITY,
                        severity=AlertSeverity.OPPORTUNITY,
                        sku=sku,
                        tienda_id=origin.tienda_id,
                        mensaje=(
                            f"Oportunidad de transferencia SKU {sku}: reasignar {suggested_qty} "
                            f"unidades desde {origin.tienda_id} ({origin.ciudad}) "
                            f"hacia {destination.tienda_id} ({destination.ciudad})."
                        ),
                        dci=calculate_item_kpi(origin).dci,
                        stock_actual=origin.stock_actual,
                        tienda_destino=destination.tienda_id,
                        unidades_sugeridas=suggested_qty,
                    )
                    transfers.append(alert)
                    available_to_send -= suggested_qty
                    if available_to_send <= 0:
                        break

        return transfers

    def compute_metrics(
        self, items: List[InventoryItem], ground_truth: List[str]
    ) -> Dict[str, float]:
        """Calcula precisión, recall y F1-score frente al ground truth.

        Args:
            items: Lista de InventoryItem.
            ground_truth: Lista de etiquetas esperadas.

        Returns:
            Diccionario con precision, recall y f1_score.
        """
        if len(items) != len(ground_truth):
            raise ValueError("La cantidad de ítems y etiquetas de ground truth debe coincidir.")

        predictions = [self.evaluate_item(item).alert_type.value for item in items]
        classes = ["CRITICAL_STOCKOUT", "WARNING_LOW_STOCK", "OVERSTOCK_RISK", "HEALTHY"]

        f1_scores: List[float] = []
        for cls in classes:
            tp = sum(1 for p, y in zip(predictions, ground_truth) if p == cls and y == cls)
            fp = sum(1 for p, y in zip(predictions, ground_truth) if p == cls and y != cls)
            fn = sum(1 for p, y in zip(predictions, ground_truth) if p != cls and y == cls)

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = (
                (2 * precision * recall) / (precision + recall)
                if (precision + recall) > 0
                else 0.0
            )
            f1_scores.append(f1)

        macro_f1 = sum(f1_scores) / len(f1_scores)
        return {
            "macro_f1": round(macro_f1, 4),
            "classes_evaluated": len(classes),
        }
