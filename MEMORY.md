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
- **Resultados obtenidos:** Pylint 10.00/10.0, Coverage 88% (30 tests pasando), Macro F1 0.865, $\Delta T = 79{,}04\%$.
- **Estado:** CERTIFICADO.

### ADR-004: Estandarización de Identificador de Producto (SKU)
- **Decisión:** Adoptar de manera estricta y universal la convención `MODELO-TALLA-COLOR` (ej. `CAMISA_OXFORD-M-AZUL`, `JEAN_SLIM-32-INDIGO`).
- **Estado:** IMPLEMENTADO EN CÓDIGO, DATASET Y DOCUMENTACIÓN.

### ADR-005: Generación Automatizada de Órdenes de Reposición en Excel
- **Decisión:** Implementar un módulo desacoplado (`src/replenishment_exporter.py`) que procese las alertas de desabastecimiento (`CRITICAL_STOCKOUT` y `WARNING_LOW_STOCK`), calcule el volumen de reposición según lead times regionales de Colombia y stock de seguridad, y exporte `logs/reporte_reposicion_inventario.xlsx` con dos hojas (`Orden_Reposicion_SKU` y `Resumen_Ejecutivo_Tiendas`), semaforización visual y formato de moneda COP.
- **Estado:** IMPLEMENTADO Y CERTIFICADO (4 pruebas unitarias dedicadas, 95% cobertura en módulo, 203 referencias priorizadas).

### ADR-006: Gestión Ágil de Proyectos (Puntos de Historia, Burndown y Velocidad)
- **Decisión:** Incorporar los artefactos formales de seguimiento ágil solicitados en la retroalimentación docente: desglose de los 35 Puntos de Historia en 11 Historias de Usuario (`HU-01` a `HU-11`) distribuidas en 4 sprints, gráficas de Burndown general y por sprint, e Informe de Velocidad comparada ($1{,}59\text{ PH/h}$ frente a $0{,}33\text{ PH/h}$ tradicional, aceleración de $4{,}82\times$), respaldado por `scripts/generar_metricas_agiles.py` y `logs/metricas_gestion_proyecto.json`.
- **Estado:** IMPLEMENTADO, VERIFICADO EN SUITE DE PRUEBAS Y COMPILADO EN ENTREGA 2.

### ADR-007: Reorganización Modular Multi-Proyecto y Desacoplamiento Agnóstico
- **Decisión:** Aislamiento del caso de estudio de retail en `case_studies/retail_inventory/` y limpieza de toda regla fija de retail/SKU en los descriptores de agentes de `.opencode/agents/`, `AGENTS.md` y `ANTIGRAVITY.md`, convirtiendo la raíz de `SDLC-AI` en un motor multi-proyecto universal.
- **Estado:** IMPLEMENTADO Y VERIFICADO (`./run.sh all`).

### ADR-008: Experimento Controlado A/B en Caso de Estudio `todo_list`
- **Decisión:** Ejecutar una comparación empírica controlada entre dos sesiones aisladas resolviendo el mismo prompt en lenguaje natural (aplicación Web local de Lista de Tareas con grafo de dependencias y persistencia JSON): Sesión A en línea base sin arnés (`benchmarks/todo_list/sesion_a_baseline/`, conv ID `3876d820-f32e-45f5-a376-78f8c376c442`) frente a Sesión B con arnés SDLC-AI (`case_studies/todo_list/`, conv ID `286ff638-251c-4dea-b35c-164ef3975010`), auditadas con `pylint`, `pytest-cov` y una batería ciega de 10 pruebas (`benchmarks/todo_list/blind_chaos_suite.py`).
- **Resultados medidos:** Sesión A ($474{,}0\text{ s}$, Pylint $8{,}92/10$ con 69 alertas, cobertura $75{,}0\%$, batería ciega $7/10$) vs. Sesión B ($901{,}0\text{ s}$, Pylint $10{,}00/10$ con 0 alertas, cobertura $97{,}0\%$, batería ciega $10/10$).
- **Estado:** COMPLETADO, AUDITADO Y DOCUMENTADO EN `docs/agent_efficiency_benchmark.json` Y ENTREGA 2.

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
- [x] **Benchmark agéntico A/B (`todo_list`):** ejecutada y documentada la comparación
  entre sesión sin arnés y sesión con arnés SDLC-AI en `docs/agent_efficiency_benchmark.json`
  y `benchmarks/todo_list/`.

- [x] **Sprint 1 (Ingesta y KPIs):** `data_ingestion.py`, `kpi_calculator.py`, 12 pruebas unitarias.
- [x] **Sprint 2 (Motor de Alertas y Reposición):** `alert_engine.py`, transferencias multitienda, `replenishment_exporter.py` (Excel con 203 productos), 9 pruebas, F1-score >= 0.80.
- [x] **Sprint 3 (Integración Gemini Pro):** `gemini_reporter.py`, fallback determinista, 5 pruebas.
- [x] **Sprint 4 (DevOps, Arnés y Evaluación):** `requirements.txt`, `run.sh`, `main.py`, `pyproject.toml`, arnés `test_agent_harness.py` (4 pruebas), $\Delta T = 79{,}04\%$ (resultado preliminar sobre referencia paramétrica). Total repositorio: **60 pruebas automatizadas pasando (4 arnés + 18 docx + 27 retail + 11 todo_list) más 10/10 en batería ciega de caos**.
- [x] **Entrega 2 Auditada (`.docx`):** `Entregables/SDLC-AI_Tesis_Entrega2.docx` compilado con Tabla de Contenidos, 10 figuras a 300 DPI (incluyendo Figura 2 vectorial sin solapamientos y Figuras 9–10 de capturas web), 6 tablas con bordes negros APA 7, 11 referencias verificadas y orden APA 7 (`# REFERENCIAS` seguido de `# ANEXOS`).
- [ ] **Entrega 3 Final (15 de diciembre de 2026):** Consolidar todos los avances de la Entrega 2 en `SDLC-AI_Tesis_Entrega3_Final.md/.docx/.pdf`, opcionalmente cronometrar retrabajo humano o réplica adicional del benchmark, y preparar diapositivas de sustentación.

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
