"""Pruebas de integración E2E para src/main.py."""

from src.main import run_pipeline


def test_run_pipeline_e2e():
    """Verifica la ejecución del pipeline integral end-to-end."""
    results = run_pipeline("data/synthetic_retail_data.csv")
    assert results["total_records_processed"] == 450
    assert results["total_alerts_emitted"] == 450
    assert results["hypothesis_validated"] is True
    assert results["delta_t_reduction_percentage"] >= 30.0
