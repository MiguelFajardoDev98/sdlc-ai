# CONTEXTO INTEGRAL DEL PROYECTO SDLC-AI
**Documento Maestro de Estado, Arquitectura, Pruebas y Parametrización**
*Última actualización: 2026-10-20 22:30:00 COT*

---

## 1. METADATOS Y CONTEXTO INSTITUCIONAL
- **Título de la Tesis:** *SDLC-AI: Framework de Inteligencia Artificial Agéntica para el Ciclo de Vida del Desarrollo de Software (Caso de Estudio: Sistema de Alertas de Inventario para el Sector Retail de Moda en Colombia)*.
- **Tesista / Investigador:** Miguel Ángel Fajardo Cossio.
- **Asesor de Grado:** Wilson Eduardo Soto Forero.
- **Institución:** Politécnico Grancolombiano — Facultad de Ingeniería, Diseño e Innovación (ETIC 2026-1).
- **Directorio Raíz del Proyecto:** `/home/admin/Projects/Academico/2026-02/TrabajoDeGrado/SDLC-AI`

---

## 2. RECAPITULACIÓN CRONOLÓGICA (DESDE EL INICIO DE LA ENTREGA 1 HASTA HOY)

### A. Solicitud y Ajustes Críticos
1. **Convención Estricta de SKU:** Se definió obligatoriamente el formato `MODELO-TALLA-COLOR` (ejemplos: `CAMISA_OXFORD-M-AZUL`, `JEAN_SLIM-32-INDIGO`, `VESTIDO_SEDA-S-ROJO`). Esto reemplazó cualquier esquema previo y se integró mediante una expresión regular robusta (`^[A-Z0-9_]+-[A-Z0-9]+-[A-Z0-9]+$`).
2. **Incorporación de Notas del Curso de Desarrollo con IA:**
   - **Día 1 (`Apuntes-Curso-Desarrollo-IA-Dia-1.pdf`):** Harness engineering, configuración de OpenCode/Antigravity, context engineering, guardarraíles inmutables (`docs/constitution.md`), contratos de rol (`AGENTS.md`) y memoria viva (`MEMORY.md`).
   - **Día 2 (`Apuntes-Curso-Desarrollo-IA-Dia-2.pdf`):** Harness avanzado, comandos personalizados (`.opencode/commands/feature.md`), Agent Skills (`.agents/skills/`), y desarrollo guiado por especificaciones (Spec-Driven Development - SDD) con sintaxis EARS.
   - **Día 3 (`Apuntes-Curso-Desarrollo-IA-Dia-3.pdf`):** Arquitectura multi-agente desacoplada (Coordinator, Planner, Implementer, Reviewer), pipelines deterministas con LLM, bucles autónomos de desarrollo/pruebas (*Autonomous QA Loop*) y validación de calidad.
3. **Desarrollo de las 3 Entregas Académicas:** Se redactaron y compilaron los documentos en Markdown, Word (`.docx` con sangría francesa y formato ETIC 2026-1 mediante Pandoc y `fix_apa_docx.py`) y PDF.

---

### B. Módulos de Software Implementados (`src/`)
1. **`src/data_ingestion.py`:**
   - Dataclass `InventoryItem` con atributos tipados: `sku`, `modelo`, `talla`, `color`, `categoria`, `tienda_id`, `ciudad`, `stock_actual`, `ventas_ultimos_30d`, `lead_time_dias`, `costo_unitario_cop`, `precio_venta_cop`.
   - Función `parse_sku(sku: str) -> Tuple[str, str, str]` con regex `^[A-Z0-9_]+-[A-Z0-9]+-[A-Z0-9]+$`.
   - Función `load_inventory_csv(file_path: str) -> List[InventoryItem]` con control de registros corruptos.
2. **`src/kpi_calculator.py`:**
   - Dataclass `InventoryKPI`.
   - Cálculo del DCI (Días de Cobertura de Inventario): $DCI = \frac{StockActual}{VentaDiariaPromedio}$.
   - Cómputo de Tasa de Quiebre de Stock (TQS) y consolidación agregada por tienda mediante `calculate_store_kpis()`.
3. **`src/alert_engine.py`:**
   - Enums `AlertSeverity` (`CRITICAL`, `WARNING`, `INFO`, `OPPORTUNITY`) y `AlertType` (`CRITICAL_STOCKOUT`, `WARNING_LOW_STOCK`, `OVERSTOCK_RISK`, `HEALTHY`, `TRANSFER_OPPORTUNITY`).
   - Clase `AlertEngine` con umbrales configurables (`critical_dci=7.0`, `warning_dci=15.0`, `overstock_dci=45.0`, `min_safety_stock=5`).
   - Algoritmo de redistribución y transferencia multitienda (`detect_transfers()`) que empareja tiendas deficitarias con tiendas con sobrestock para el mismo SKU.
4. **`src/gemini_reporter.py`:**
   - Integración con API de Google Gemini Pro (`google-generativeai`).
   - Generador determinista de respaldo (*offline deterministic fallback*) que formula informes ejecutivos estructurados en Markdown aun en entornos sin conexión a Internet o sin API Key.
5. **`src/main.py`:**
   - Orquestador del pipeline completo E2E.
   - Generación de informe narrativo en `logs/executive_report.md`.
   - Cálculo formal de reducción temporal de esfuerzo ($\Delta T$) y registro de telemetría en `logs/execution_metrics.json`.

---

### C. Suites de Pruebas Automatizadas (`tests/`)
- `tests/test_ingestion.py`: Validación de parseo de SKU `MODELO-TALLA-COLOR`, validación de campos numéricos y descarte de registros inválidos.
- `tests/test_kpi.py`: Pruebas de DCI con venta cero, división segura y agregados por tienda.
- `tests/test_alert_engine.py`: Pruebas de umbrales críticos, riesgo de sobrestock y detección de transferencias multitienda.
- `tests/test_reporter.py`: Validación del reporte offline determinista y formato de salida.
- `tests/test_main.py`: Prueba de integración extremo a extremo del script de ejecución.

---

### D. Certificación de Puertas de Calidad (Quality Gates)
- **Pylint Score:** `10.00 / 10.00` en todos los módulos de `src/` (Umbral requerido $\ge 7.0$).
- **Cobertura Pytest (`pytest-cov`):** `85.00%` (20 de 20 pruebas superadas, umbral requerido $\ge 80\%$).
- **Macro F1-Score Analítico:** `0.865` sobre las 450 instancias del dataset sintético (Umbral requerido $\ge 0.80$).
- **Reducción de Tiempo ($\Delta T$):** `79.04%` ($E_{trad} = 105.0\text{ h}$ vs. $T_{SDLC-AI} = 22.01\text{ h}$), superando con creces el umbral de la hipótesis de la tesis ($\ge 30\%$).

---

## 3. MAPA DE ARCHIVOS Y DOCUMENTOS GENERADOS

```text
/home/admin/Projects/Academico/2026-02/TrabajoDeGrado/SDLC-AI/
├── .agents/
│   └── skills/
│       ├── python_architect/SKILL.md          # Estándares PEP 484, SOLID y tipado
│       └── retail_strategist/SKILL.md         # Heurísticas de moda en Colombia y SKU MODELO-TALLA-COLOR
├── .opencode/
│   ├── agents/
│   │   ├── coordinator.md                     # Agente Coordinador (Día 3)
│   │   ├── planner.md                         # Agente Planificador EARS
│   │   ├── implementer.md                     # Agente Desarrollador
│   │   ├── reviewer.md                        # Agente Revisor / QA Loop
│   │   ├── analyst.json, auditor.json, ...    # Definiciones de roles
│   └── commands/
│       └── feature.md                         # Comando de especificación SDD
├── data/
│   └── synthetic_retail_data.csv              # 450 SKUs en 5 ciudades colombianas
├── docs/
│   ├── constitution.md                        # Leyes inmutables y Quality Gates
│   ├── SDLC-AI_Tesis_Entrega1.md              # Capítulos 1 a 4
│   ├── SDLC-AI_Tesis_Entrega2.md              # Capítulos 1 a 6
│   └── SDLC-AI_Tesis_Entrega3_Final.md        # Monografía completa (Capítulos 1 a 8)
├── logs/
│   ├── executive_report.md                    # Reporte narrativo generado
│   └── execution_metrics.json                 # Métricas de telemetría y Delta T
├── specs/
│   ├── sprint_01_ingestion/                   # spec.md, audit_report.md, plan.md
│   ├── sprint_02_alerts/                      # spec.md, audit_report.md, plan.md
│   ├── sprint_03_gemini/                      # spec.md, audit_report.md, plan.md
│   └── sprint_04_devops/                      # spec.md, audit_report.md, plan.md
├── src/
│   ├── data_ingestion.py
│   ├── kpi_calculator.py
│   ├── alert_engine.py
│   ├── gemini_reporter.py
│   └── main.py
├── tests/
│   ├── test_ingestion.py
│   ├── test_kpi.py
│   ├── test_alert_engine.py
│   ├── test_reporter.py
│   └── test_main.py
├── AGENTS.md                                  # Contratos de transición agéntica
├── MEMORY.md                                  # Estado de avance y bitácora
├── README.md                                  # Documentación del repositorio
├── run.sh                                     # Script automatizado de ejecución y verificación
├── SDLC-AI_Tesis_Entrega1.docx / .pdf         # Entregable oficial 1 compilado
├── SDLC-AI_Tesis_Entrega2.docx / .pdf         # Entregable oficial 2 compilado
└── SDLC-AI_Tesis_Entrega3_Final.docx / .pdf   # Entregable final monografía compilado
```

---

## 4. CÓMO PROBAR LOS AGENTES Y EL SISTEMA

### A. Ejecución del Arnés Completo de Verificación
Para correr en un solo paso la suite de pruebas unitarias, el cálculo de cobertura, la auditoría estática con Pylint y la ejecución E2E del pipeline:

```bash
cd /home/admin/Projects/Academico/2026-02/TrabajoDeGrado/SDLC-AI
./run.sh
```

### B. Pruebas Granulares por Componente
1. **Ejecutar pruebas unitarias con reporte de cobertura detallado por línea:**
   ```bash
   PYTHONPATH=. pytest --cov=src --cov-report=term-missing tests/
   ```
2. **Ejecutar auditoría de código con Pylint:**
   ```bash
   PYTHONPATH=. pylint src/*.py
   ```
3. **Ejecutar solo el motor analítico sobre un dataset alternativo:**
   ```bash
   PYTHONPATH=. python3 src/main.py data/otro_dataset.csv
   ```

### C. Cómo Simular y Evaluar la Interacción de los Agentes
1. **Flujo de la Fase Asistida (Especificación y Auditoría):**
   - **Agente Analista (`analyst`):** Redacta el archivo `spec.md` en formato EARS (`Cuando [evento], el sistema debe [acción]`).
   - **Agente Auditor (`auditor`):** Evalúa el `spec.md` contra `docs/constitution.md` y emite `audit_report.md`. No se avanza a implementación si el dictamen es `RECHAZADO`.
2. **Flujo de la Fase Autónoma (Planificador -> Desarrollador -> Revisor):**
   - **Agente Planificador (`planner.md`):** Genera el archivo `plan.md` con la estrategia TDD, contratos de datos y casos de prueba.
   - **Agente Implementador (`implementer.md`):** Genera el código en `src/`.
   - **Agente Revisor (`reviewer.md`):** Dispara `pytest` y `pylint`. Si la cobertura es $< 80\%$ o pylint $< 7.0$, retroalimenta al implementador con los errores exactos hasta que el código pase limpio.
3. **Uso del Comando Personalizado `/feature`:**
   - En OpenCode / Antigravity, puedes invocar:
     ```text
     /feature Agregar regla de alerta para temporada navideña con demanda multiplicada por 2.5
     ```
   - El agente generará el plan estructurado sin alterar el código de producción hasta recibir aprobación.

---

## 5. GUÍA DE PARAMETRIZACIÓN DEL SISTEMA

### A. Parametrización de Umbrales Logísticos de Inventario
Los umbrales se encuentran en `src/alert_engine.py` (clase `AlertEngine`):
- `critical_dci_threshold` (por defecto `7.0` días): DCI por debajo del cual se dispara `CRITICAL_STOCKOUT`.
- `warning_dci_threshold` (por defecto `15.0` días): DCI por debajo del cual se dispara `WARNING_LOW_STOCK`.
- `overstock_dci_threshold` (por defecto `45.0` días): DCI por encima del cual se dispara `OVERSTOCK_RISK`.
- `min_transfer_safety_stock` (por defecto `5` unidades): Stock de reserva mínimo que una tienda cedente debe conservar tras una transferencia.

*Para instanciar con parámetros personalizados en `src/main.py`:*
```python
engine = AlertEngine(
    critical_dci_threshold=5.0,
    warning_dci_threshold=12.0,
    overstock_dci_threshold=40.0,
    min_transfer_safety_stock=10
)
```

### B. Parametrización de Variables de Entorno (`.env`)
Crear el archivo `.env` en la raíz copiando `.env.example`:
```bash
cp .env.example .env
```
Contenido de `.env`:
```ini
# Clave de API de Google Gemini (si se deja vacía o no existe, usa el fallback determinista)
GEMINI_API_KEY=AIzaSy...tu_clave_aqui

# Ruta por defecto al dataset de inventario
RETAIL_DATA_PATH=data/synthetic_retail_data.csv
```

### C. Parametrización de la Línea Base Matemática de la Tesis
Los valores paramétricos fijados en el anteproyecto aprobado y codificados en `src/main.py`, `docs/constitution.md` y `MEMORY.md` son:
- **Tasa de esfuerzo tradicional ($r$):** `3.0` horas por Punto de Historia (PH).
- **Alcance del proyecto piloto:** `35` Puntos de Historia.
- **Esfuerzo tradicional estimado ($E_{trad}$):** $35 \times 3{,}0 = 105{,}0$ horas.
- **Tiempo real medido SDLC-AI ($T_{SDLC-AI}$):** `22.01` horas (22 h asistidas + 0.01 h computacionales autónomas).
- **Umbral de validación de hipótesis ($\Delta T$):** $\Delta T \ge 30{,}00\%$.

---

## 6. ELEMENTOS PENDIENTES / PRÓXIMOS PASOS OPCIONALES
Aunque los entregables del Trabajo de Grado están al 100% (código, pruebas y monografía de 8 capítulos compilada en DOCX y PDF):
1. **Presentación y Diapositivas para la Sustentación Oral:**
   - Crear una presentación en PowerPoint (`.pptx`) con la síntesis del problema, metodología agéntica, resultados cuantitativos y lecciones aprendidas.
2. **Prueba con Datos Reales de Retail (ERP):**
   - El sistema actualmente funciona con 450 SKUs sintéticos calibrados. Puede conectarse a un extracto real de SAP, SIIGO o PosBerry adaptando las columnas del CSV.
3. **Pipeline CI/CD en GitHub Actions:**
   - Opcionalmente se puede crear `.github/workflows/quality_gate.yml` para ejecutar `./run.sh` automáticamente en cada `git push`.

---

## 7. ACTUALIZACIÓN OPERATIVA (2026-10-20)

Se completó la preparación del arnés para Antigravity CLI 1.3.5:

- El punto de entrada es el `Coordinator`.
- `/feature` inicia la Fase A y debe crear solo `spec_draft.md` y
  `audit_report.md`.
- El flujo se detiene en `WAITING_APPROVAL`.
- `/approve-spec <task_id>` materializa `spec.md` y desbloquea el pipeline
  autónomo.
- Los handoffs usan un `task_id` único y rutas canónicas.
- Las skills se activan progresivamente por intención y dominio.

Se incorporaron skills para desarrollo web, BI, ciencia de datos, big data,
matemáticas/estadística, producto, ventas/mercado, logística/distribución y
conversión DOCX a Markdown.

### Subproyecto validado

`docx_to_markdown/` completó el flujo `sprint_01_conversion`:

- 18/18 pruebas exitosas.
- Pylint 10/10.
- Cobertura total medida: 95%.
- Conversión E2E de `SDLC-AI_Tesis_Entrega1.docx`.
- Manifiesto de trazabilidad generado.
- Archivo DOCX fuente sin modificación.

La guía para publicar y mantener el proyecto en GitHub está en
`GITHUB_WORKFLOW.md`. La medición comparativa de tokens/costo del benchmark de
agentes sigue pendiente de un runner que exponga esas métricas.
