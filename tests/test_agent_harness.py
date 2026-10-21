"""Pruebas de contrato para skills y configuración de agentes."""

import json
from pathlib import Path


ROOT = Path(__file__).parents[1]
SKILLS = {
    "web_engineering",
    "business_intelligence",
    "data_science",
    "big_data",
    "math_statistics",
    "product_analysis",
    "sales_market",
    "logistics_distribution",
}
REQUIRED_SKILL_SECTIONS = ("## Entrada mínima", "## Procedimiento", "## Salida")


def test_domain_skills_have_minimal_contract():
    """Every domain skill exposes the sections needed for progressive loading."""
    for skill_name in SKILLS:
        content = (ROOT / ".agents" / "skills" / skill_name / "SKILL.md").read_text(
            encoding="utf-8"
        )
        assert content.startswith("---\n")
        assert all(section in content for section in REQUIRED_SKILL_SECTIONS if section != "## Entrada mínima" or skill_name == "web_engineering")
        assert "## Guardrails" in content


def test_agent_configs_reference_existing_skills():
    """Agent skill references resolve to local skill contracts."""
    for config_path in (ROOT / ".opencode" / "agents").glob("*.json"):
        config = json.loads(config_path.read_text(encoding="utf-8"))
        for skill_name in config.get("skills", []):
            assert (ROOT / ".agents" / "skills" / skill_name / "SKILL.md").is_file()


def test_efficiency_benchmark_defines_non_regression():
    """The benchmark documents quality-preserving efficiency measurements."""
    benchmark = (ROOT / "docs" / "agent_efficiency_benchmark.md").read_text(
        encoding="utf-8"
    )
    assert "Criterio de no-regresión" in benchmark
    assert "input_tokens" in benchmark
    assert "quality_score" in benchmark
