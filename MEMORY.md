# MEMORY.MD: ESTADO VIVO, CRONOGRAMA Y TRAZABILIDAD (SDLC-AI)

## 1. METADATOS DEL PROYECTO
- **Proyecto:** SDLC-AI: Framework de Inteligencia Artificial Agéntica para el Ciclo de Vida del Desarrollo de Software (Caso de Estudio: Sistema de Alertas de Inventario para el Sector Retail de Moda en Colombia).
- **Investigador:** Miguel Ángel Fajardo Cossio.
- **Asesor:** Wilson Eduardo Soto Forero.
- **Institución:** Politécnico Grancolombiano — Facultad de Ingeniería, Diseño e Innovación.
- **Convención de SKU:** `MODELO-TALLA-COLOR` (ej. `CAMISA_OXFORD-M-AZUL`).
- **Estado General:** **IMPLEMENTACIÓN COMPLETA DEL FRAMEWORK Y DEL SUBPROYECTO DOCX; SUITES DE PRUEBAS FINALIZADAS.**

---

## 2. CRONOGRAMA DE ENTREGAS ACADÉMICAS FORMALES

| Hito / Entrega Académica | Ventana de Ejecución y Entrega | Alcance de Software | Alcance Documental (Formato ETIC 2026-1) | Estado |
| :--- | :--- | :--- | :--- | :--- |
| **ENTREGA 1** | **2026-10-17 al 2026-10-24** | Harness Antigravity, Skills (`retail_strategist`, `python_architect`), SRS Sprint 1, `data_ingestion.py`, `kpi_calculator.py`, tests (`cov >= 80%`). | Capítulos 1, 2, 3 y 4 (Metodología inicial y formalización línea base). | 🟢 **COMPLETADA** |
| **ENTREGA 2** | **2026-11-09 al 2026-11-16** | Sprint 2 (`alert_engine.py`), Sprint 3 (`gemini_reporter.py`), Loop cerrado QA (`F1 >= 0.80`, `cov >= 80%`, `pylint 10.0`). | Capítulos 1 al 6 (Metodología completa, Arquitectura de Agentes, Desarrollo y QA). | 🟢 **COMPLETADA** |
| **ENTREGA 3** | **2026-12-06 al 2026-12-13** | Sprint 4 (DevOps, empaquetado, `requirements.txt`, `run.sh`), cálculo empírico de $\Delta T = 79{,}04\% \ge 30\%$, repositorio GitHub público. | Tesis completa (Capítulos 1 a 8: Resultados comparativos, Conclusiones y Trabajo Futuro). | 🟢 **COMPLETADA** |

---

## 3. REGISTRO DE DECISIONES DE ARQUITECTURA (ADRs)

### ADR-001: Arquitectura Híbrida en Dos Fases con Especificación Front-Loaded
- **Decisión:** Separar el proceso en (1) Fase de Especificación Asistida (Investigador + Analista + Auditor) y (2) Pipeline Autónomo de Ejecución (Arquitecto -> Desarrollador -> Tester -> DevOps).
- **Estado:** APROBADO Y VALIDADO.

### ADR-002: Formalización Paramétrica de Línea Base Tradicional
- **Decisión:** Constante paramétrica $r = 3{,}0\text{ h/PH}$ ($E_{trad} = \sum PH_i \times 3{,}0\text{ h}$). Para 35 PH, $E_{trad} = 105{,}0\text{ h}$.
- **Estado:** APROBADO Y APLICADO.

### ADR-003: Quality Gates Innegociables en Suite de Pruebas
- **Decisión:** Imponer `pylint score >= 7.0/10.0`, `pytest-cov >= 80%`, `F1-score >= 0.80` y $\Delta T \ge 30\%$.
- **Resultados obtenidos:** Pylint 10.00/10.0, Coverage 85%, Macro F1 0.865, $\Delta T = 79{,}04\%$.
- **Estado:** CERTIFICADO.

### ADR-004: Estandarización de Identificador de Producto (SKU)
- **Decisión:** Adoptar de manera estricta y universal la convención `MODELO-TALLA-COLOR` (ej. `CAMISA_OXFORD-M-AZUL`, `JEAN_SLIM-32-INDIGO`).
- **Estado:** IMPLEMENTADO EN CÓDIGO, DATASET Y DOCUMENTACIÓN.

---

## 4. ESTADO DE LOS SPRINTS DE DESARROLLO

## 4.1 GOBERNANZA DE SKILLS Y EFICIENCIA AGÉNTICA

- [x] **Skills de dominio:** se incorporaron `web_engineering`,
  `business_intelligence`, `data_science`, `big_data`, `math_statistics`,
  `product_analysis`, `sales_market` y `logistics_distribution`.
- [x] **Activación selectiva:** cada skill declara su activación, entrada mínima,
  guardrails y salida; los roles cargan solo las familias pertinentes.
- [x] **Política de contexto:** `AGENTS.md` exige carga progresiva, handoffs
  mínimos, salidas estructuradas y no-regresión de calidad.
- [x] **Integración operativa Antigravity:** Coordinator, estados, handoffs,
  aprobación explícita de `spec.md` y comandos `/feature`, `/status` y
  `/approve-spec` documentados en `ANTIGRAVITY.md`.
- [x] **Subproyecto DOCX a Markdown:** `docx_to_markdown/` completó Fases A-E
  con ruta canónica `sprint_01_conversion`.
- [ ] **Benchmark agéntico:** pendiente ejecutar la comparación baseline vs.
  arnés optimizado definida en `docs/agent_efficiency_benchmark.md`.

- [x] **Sprint 1 (Ingesta y KPIs):** `data_ingestion.py`, `kpi_calculator.py`, 12 pruebas unitarias.
- [x] **Sprint 2 (Motor de Alertas):** `alert_engine.py`, transferencias multitienda, 5 pruebas, F1-score >= 0.80.
- [x] **Sprint 3 (Integración Gemini Pro):** `gemini_reporter.py`, fallback determinista, 2 pruebas.
- [x] **Sprint 4 (DevOps y Evaluación):** `requirements.txt`, `run.sh`, `main.py`, 1 prueba E2E, $\Delta T = 79{,}04\%$.

### 4.2 Subproyecto `docx_to_markdown`

- Estado: **COMPLETED**.
- Artefactos: `spec.md`, `plan.md`, código modular, tests, manifiesto y salida
  Markdown real.
- Resultado verificado: 18/18 pruebas, Pylint 10/10, cobertura total 95%,
  conversión E2E exitosa y fuente DOCX inmutable.

---

## 5. TELEMETRÍA Y MÉTRICAS VALIDADAS (`logs/execution_metrics.json`)
```json
{
  "dataset_evaluated": "data/synthetic_retail_data.csv",
  "total_records_processed": 450,
  "total_alerts_emitted": 450,
  "transfer_opportunities_detected": 63,
  "tasa_quiebre_stock_pct": 7.78,
  "valor_total_inventario_cop": 1236505000.0,
  "pipeline_execution_seconds": 0.01,
  "traditional_baseline_hours": 105.0,
  "sdlc_ai_total_hours": 22.01,
  "delta_t_reduction_percentage": 79.04,
  "hypothesis_validated": true
}
```
