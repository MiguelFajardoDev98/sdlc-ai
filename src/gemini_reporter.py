"""Módulo de Reportería Narrativa de Inventario con Google Gemini Pro.

Este módulo toma las alertas y KPIs calculados y genera un reporte ejecutivo
en lenguaje natural estructurado, ideal para la toma de decisiones gerenciales
en el sector retail de moda en Colombia.
"""

import logging
import os
from typing import Any, Dict, List, Optional

try:
    from src.alert_engine import Alert, AlertType
except ImportError:
    from alert_engine import Alert, AlertType  # type: ignore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiInventoryReporter:
    """Generador de reportes ejecutivos narrativos utilizando Gemini Pro o fallback."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-1.5-pro",
    ) -> None:
        """Inicializa el cliente de reportería con la clave de API o variable de entorno."""
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model_name = model_name
        self.client = None

        if self.api_key:
            try:
                # Import dinámico para no forzar dependencia estricta si no hay API key
                import google.generativeai as genai  # pylint: disable=import-outside-toplevel

                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(self.model_name)
                logger.info("Cliente Gemini Pro inicializado exitosamente.")
            except ImportError:
                logger.warning(
                    "Librería google-generativeai no instalada. Usando modo determinista."
                )

    def build_context_prompt(
        self,
        alerts: List[Alert],
        store_kpis: Dict[str, Any],
        transfers: Optional[List[Alert]] = None,
    ) -> str:
        """Construye el prompt estructurado para alimentar al LLM.

        Args:
            alerts: Lista de alertas generadas.
            store_kpis: Métricas agregadas de inventario.
            transfers: Lista opcional de oportunidades de transferencia.

        Returns:
            Prompt en texto plano formateado.
        """
        transfers = transfers or []
        critical_count = sum(
            1 for a in alerts if a.alert_type == AlertType.CRITICAL_STOCKOUT
        )
        warning_count = sum(
            1 for a in alerts if a.alert_type == AlertType.WARNING_LOW_STOCK
        )
        overstock_count = sum(
            1 for a in alerts if a.alert_type == AlertType.OVERSTOCK_RISK
        )

        val_inv = store_kpis.get('valor_total_inventario', 0.0)
        return (
            "Eres el Asesor Senior de Operaciones y Cadena de Suministro para Retail de Moda.\n"
            "Analiza los siguientes indicadores consolidados y genera un informe ejecutivo:\n"
            f"- Total SKUs evaluados: {store_kpis.get('total_skus', 0)}\n"
            f"- Tasa de Quiebre de Stock: {store_kpis.get('tasa_quiebre_stock_pct', 0.0)}%\n"
            f"- Valor Total de Inventario: ${val_inv:,.2f} COP\n"
            f"- Alertas Críticas (Quiebre): {critical_count}\n"
            f"- Alertas de Bajo Stock: {warning_count}\n"
            f"- Alertas de Sobrestock: {overstock_count}\n"
            f"- Oportunidades de Transferencia Intertiendas: {len(transfers)}\n\n"
            "El formato del reporte debe incluir:\n"
            "1. Resumen Ejecutivo y Diagnóstico Global\n"
            "2. Análisis de Quiebres Críticos y Riesgo de Facturación\n"
            "3. Plan de Transferencias y Balanceo Multitienda\n"
            "4. Recomendaciones Estratégicas para la Temporada Comercial en Colombia\n"
        )

    def generate_narrative_report(
        self,
        alerts: List[Alert],
        store_kpis: Dict[str, Any],
        transfers: Optional[List[Alert]] = None,
    ) -> str:
        """Genera el reporte ejecutivo completo.

        Args:
            alerts: Alertas generadas por el motor.
            store_kpis: Indicadores agregados de inventario.
            transfers: Oportunidades de transferencia identificadas.

        Returns:
            Texto del reporte ejecutivo estructurado en Markdown.
        """
        transfers = transfers or []
        prompt = self.build_context_prompt(alerts, store_kpis, transfers)

        if self.client:
            try:
                response = self.client.generate_content(prompt)
                if response and response.text:
                    return response.text
            except Exception as err:  # pylint: disable=broad-except
                logger.warning("Fallo en llamada a Gemini API (%s). Usando fallback.", err)

        # Fallback determinista enriquecido de alta calidad
        return self._generate_deterministic_report(alerts, store_kpis, transfers)

    def _generate_deterministic_report(
        self,
        alerts: List[Alert],
        store_kpis: Dict[str, Any],
        transfers: List[Alert],
    ) -> str:
        """Genera el reporte analítico estructurado en modo local/offline."""
        critical_alerts = [
            a for a in alerts if a.alert_type == AlertType.CRITICAL_STOCKOUT
        ]
        tqs = store_kpis.get("tasa_quiebre_stock_pct", 0.0)
        total_skus = store_kpis.get("total_skus", 0)
        valor_total = store_kpis.get("valor_total_inventario", 0.0)
        tol_status = (
            "por encima del umbral de tolerancia del 5%"
            if tqs > 5.0
            else "en rango controlado"
        )

        lines = [
            "# INFORME EJECUTIVO: DIAGNÓSTICO DE INVENTARIO Y ALERTAS LOGÍSTICAS",
            "**Sector:** Retail de Moda en Colombia  ",
            "**Motor Analítico:** Framework SDLC-AI — Capa de Generación Narrativa",
            "",
            "## 1. Resumen Ejecutivo y Diagnóstico Global",
            (
                f"Se ha completado el análisis exhaustivo sobre un universo de **{total_skus} "
                f"SKUs activos** (convención `MODELO-TALLA-COLOR`), valorizados en "
                f"**${valor_total:,.2f} COP**. La red comercial registra una **Tasa de Quiebre "
                f"de Stock (TQS) del {tqs:.2f}%**, situándose {tol_status}."
            ),
            "",
            "## 2. Análisis de Quiebres Críticos y Riesgo Comercial",
            (
                f"Se identificaron **{len(critical_alerts)} eventos de quiebre crítico** "
                "(DCI < 7 días o stock en cero con demanda activa). Las referencias con mayor "
                "urgencia de reabastecimiento corresponden a tallas centrales (S y M)."
            ),
        ]

        if critical_alerts:
            lines.append("\n**Top Referencias en Quiebre Crítico:**")
            for alert in critical_alerts[:5]:
                item_txt = (
                    f"- SKU `{alert.sku}` en {alert.tienda_id}: "
                    f"Stock = {alert.stock_actual} un."
                )
                lines.append(item_txt)

        lines.extend([
            "",
            "## 3. Plan de Transferencias y Balanceo Multitienda",
            (
                f"El motor detectó **{len(transfers)} oportunidades viables de redistribución**, "
                "permitiendo abastecer tiendas desabastecidas mediante sobrestocks sin incurrir "
                "en compras adicionales a proveedores."
            ),
        ])

        if transfers:
            lines.append("\n**Transferencias Sugeridas:**")
            for t in transfers[:5]:
                lines.append(f"- {t.mensaje}")

        lines.extend([
            "",
            "## 4. Recomendaciones Estratégicas para la Temporada Comercial",
            "1. **Priorización de Tallas Centrales:** Concentrar reposición en tallas S y M.",
            "2. **Ejecución Inmediata de Transferencias:** Reducir tránsito a menos de 48h.",
            "3. **Monitoreo Continuo:** Ejecutar el pipeline SDLC-AI de forma automatizada.",
        ])

        return "\n".join(lines)
