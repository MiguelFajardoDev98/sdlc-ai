"""Pruebas unitarias para el módulo de reportería narrativa Gemini Pro."""

from src.alert_engine import Alert, AlertSeverity, AlertType
from src.gemini_reporter import GeminiInventoryReporter


def _sample_inputs():
    """Returns the smallest representative reporter input."""
    alerts = [
        Alert(AlertType.CRITICAL_STOCKOUT, AlertSeverity.CRITICAL, "M-S-A", "T1", "Msg", 2.0, 1),
        Alert(AlertType.OVERSTOCK_RISK, AlertSeverity.INFO, "M-M-B", "T1", "Msg", 50.0, 5),
    ]
    kpis = {
        "total_skus": 2,
        "tasa_quiebre_stock_pct": 50.0,
        "valor_total_inventario": 1000000.0,
    }
    return alerts, kpis


def test_reporter_build_prompt():
    """Verifica que el prompt se construya con todas las variables necesarias."""
    reporter = GeminiInventoryReporter()
    alerts = [
        Alert(AlertType.CRITICAL_STOCKOUT, AlertSeverity.CRITICAL, "M-S-A", "T1", "Msg", 2.0, 1),
        Alert(AlertType.WARNING_LOW_STOCK, AlertSeverity.WARNING, "M-M-B", "T1", "Msg", 10.0, 5),
        Alert(AlertType.OVERSTOCK_RISK, AlertSeverity.INFO, "M-L-C", "T1", "Msg", 50.0, 10),
    ]
    kpis = {
        "total_skus": 2,
        "tasa_quiebre_stock_pct": 50.0,
        "valor_total_inventario": 1000000.0,
    }
    prompt = reporter.build_context_prompt(alerts, kpis)
    assert "Tasa de Quiebre de Stock: 50.0%" in prompt
    assert "Alertas Críticas (Quiebre): 1" in prompt
    assert "Alertas de Sobrestock: 1" in prompt


def test_reporter_generate_deterministic_report():
    """Verifica la generación del reporte en modo fallback/offline."""
    reporter = GeminiInventoryReporter()
    alerts = [
        Alert(AlertType.CRITICAL_STOCKOUT, AlertSeverity.CRITICAL, "CAMISA_OXFORD-M-AZUL", "T001", "Msg", 0.0, 0),
    ]
    transfers = [
        Alert(
            AlertType.TRANSFER_OPPORTUNITY,
            AlertSeverity.OPPORTUNITY,
            "CAMISA_OXFORD-M-AZUL",
            "T002",
            "Transferir 10 unidades de T002 a T001",
            100.0,
            50,
            tienda_destino="T001",
            unidades_sugeridas=10,
        )
    ]
    kpis = {
        "total_skus": 1,
        "tasa_quiebre_stock_pct": 100.0,
        "valor_total_inventario": 500000.0,
    }

    report = reporter.generate_narrative_report(alerts, kpis, transfers)
    assert "# INFORME EJECUTIVO" in report
    assert "CAMISA_OXFORD-M-AZUL" in report
    assert "Transferir 10 unidades" in report
    assert "Recomendaciones Estratégicas" in report


def test_reporter_uses_api_response_when_available():
    """Uses the model response when the configured client returns text."""
    reporter = GeminiInventoryReporter()

    class FakeResponse:
        """Minimal model response used to isolate the reporter."""

        text = "Reporte generado por API"

    class FakeClient:
        """Minimal Gemini client test double."""

        @staticmethod
        def generate_content(_prompt):
            return FakeResponse()

    reporter.client = FakeClient()
    alerts, kpis = _sample_inputs()
    assert reporter.generate_narrative_report(alerts, kpis) == "Reporte generado por API"


def test_reporter_falls_back_when_api_fails():
    """Returns the deterministic report when the model raises an error."""
    reporter = GeminiInventoryReporter()

    class FailingClient:
        """Client test double that simulates an unavailable provider."""

        @staticmethod
        def generate_content(_prompt):
            raise RuntimeError("provider unavailable")

    reporter.client = FailingClient()
    alerts, kpis = _sample_inputs()
    report = reporter.generate_narrative_report(alerts, kpis)
    assert "# INFORME EJECUTIVO" in report


def test_reporter_falls_back_when_api_response_is_empty():
    """Returns the deterministic report when the model has no usable text."""
    reporter = GeminiInventoryReporter()

    class EmptyClient:
        """Client test double that returns an empty response."""

        @staticmethod
        def generate_content(_prompt):
            return None

    reporter.client = EmptyClient()
    alerts, kpis = _sample_inputs()
    report = reporter.generate_narrative_report(alerts, kpis)
    assert "Diagnóstico Global" in report
