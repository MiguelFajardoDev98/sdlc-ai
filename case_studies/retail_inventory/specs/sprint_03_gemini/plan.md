# TECHNICAL DESIGN DOCUMENT (TDD) — SPRINT 3: INTEGRACIÓN GEMINI PRO

- **Autor:** Agente Arquitecto (`Architect_Agent`)
- **Fase SDLC:** Fase B — Diseño Técnico

---

## 1. COMPONENTE `src/gemini_reporter.py`

### Clase `GeminiInventoryReporter`
- `__init__(api_key: Optional[str] = None, model_name: str = "gemini-1.5-pro")`
- `build_prompt(alerts: List[Alert], store_kpis: Dict[str, Any]) -> str`: Construye el prompt con contexto sectorial de moda colombiana y métricas cuantitativas.
- `generate_narrative_report(...) -> str`: Invoca la API de Gemini si está disponible; de lo contrario, ejecuta el formateador analítico enriquecido.
