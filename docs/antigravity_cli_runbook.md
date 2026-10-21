# Runbook de ejecución con Antigravity CLI

Guía operativa para ejecutar y evaluar el proyecto **SDLC-AI** antes de las
pruebas académicas. La guía distingue entre:

1. Verificación local del software, que ya es reproducible con Python.
2. Ejecución del flujo multiagente, que depende de la instalación concreta de
   Antigravity CLI y del proveedor/modelo configurado.
3. Benchmark baseline vs. arnés optimizado para medir calidad y tokens.

## 1. Requisitos previos

- Python 3.10 o superior.
- Bash, Git y el repositorio descargado.
- Antigravity CLI instalado y autenticado en el entorno local.
- Un modelo/proveedor habilitado para las tareas agénticas.
- No guardar claves reales en el repositorio, `MEMORY.md`, prompts, respuestas ni
  logs versionados.

Desde la raíz del proyecto:

```bash
cd /home/admin/Projects/Academico/2026-02/TrabajoDeGrado/SDLC-AI
```

Verifica la versión de las herramientas con los comandos soportados por tu
instalación:

```bash
python3 --version
git --version
antigravity --version
```

Si el ejecutable tiene otro nombre, consulta su ayuda sin modificar el
repositorio:

```bash
antigravity --help
```

> La sintaxis exacta de autenticación, selección de modelo y ejecución de
> agentes puede variar entre versiones de Antigravity. Usa siempre
> `antigravity --help` como fuente para esos parámetros. El flujo, archivos y
> criterios de este documento son independientes de esa variación.

El contrato operativo que debe cargar el Coordinator está en
[`ANTIGRAVITY.md`](../ANTIGRAVITY.md). Allí se definen los estados, los handoffs,
la pausa de aprobación y los smoke tests. Los comandos conversacionales
esperados son `/feature`, `/status`, `/approve-spec` y `/reject-spec`; confirma
en `/help` si Antigravity 1.3.5 los registra con esos nombres.

## 2. Primera verificación: software local

Antes de ejecutar agentes, confirma que el producto de referencia está sano:

```bash
chmod +x run.sh
./run.sh
```

Resultado esperado:

- 26 pruebas exitosas.
- Cobertura global igual o superior a 80%; actualmente el baseline esperado es
  87%.
- Pylint igual o superior a 7.0; actualmente el baseline esperado es 10.0.
- Pipeline E2E exitoso sobre `data/synthetic_retail_data.csv`.
- Actualización de:
  - `logs/executive_report.md`
  - `logs/execution_metrics.json`

Si falla esta etapa, no ejecutes el benchmark agéntico. Corrige primero el
baseline y registra el fallo antes de continuar.

## 3. Inspección del arnés antes de una tarea

Revisa los contratos y skills que gobiernan el flujo:

```bash
sed -n '1,220p' AGENTS.md
sed -n '1,220p' docs/constitution.md
find .agents/skills -name SKILL.md -print | sort
find .opencode/agents -maxdepth 1 -type f -print | sort
python3 scripts/validate_agent_harness.py
```

Las skills se cargan progresivamente. No copies todo el contenido de todas las
skills en cada prompt. Activa únicamente las relacionadas con la tarea:

| Tipo de tarea | Skills mínimas |
|---|---|
| Nueva funcionalidad web | `web_engineering`, `python_architect` |
| KPI o dashboard | `business_intelligence`, `math_statistics` |
| Modelo predictivo | `data_science`, `math_statistics` |
| Pipeline distribuido | `big_data`, `data_science` |
| Requerimiento de producto | `product_analysis` |
| Mercado o funnel comercial | `sales_market`, `business_intelligence` |
| Inventario y distribución | `logistics_distribution`, `retail_strategist`, `math_statistics` |
| DOCX a Markdown | `document_conversion`, `python_architect` |

## 4. Flujo recomendado para desarrollar una funcionalidad

### Paso A: especificación asistida

Inicia una tarea de negocio concreta, por ejemplo:

> Agregar una regla de alerta para temporada navideña. La demanda proyectada
> debe multiplicarse por un factor configurable. No modificar código todavía.
> Genera `specs/sprint_05_seasonality/spec_draft.md` con historias de usuario,
> supuestos explícitos, tipos de datos, criterios Given-When-Then y métricas de
> aceptación. Activa `retail_strategist`, `logistics_distribution` y
> `math_statistics`.

El Analista debe producir:

```text
specs/sprint_05_seasonality/spec_draft.md
```

El estado esperado después de la auditoría es `WAITING_APPROVAL`. En ese punto
el Coordinator debe detenerse y pedir tu decisión; no debe crear `plan.md` ni
modificar `src/`.

Revisa que la especificación contenga:

- Entradas, salidas y tipos de datos.
- Fórmulas y unidades.
- Supuestos comerciales confirmados.
- Casos límite.
- Criterios automatizables.

### Paso B: auditoría

Solicita una auditoría independiente:

> Audita `specs/sprint_05_seasonality/spec_draft.md` contra
> `AGENTS.md` y `docs/constitution.md`. Rechaza términos subjetivos, formatos
> indefinidos, supuestos no validados, contradicciones y criterios no
> testeables. Genera `audit_report.md`. Solo genera `spec.md` si no existen
> observaciones críticas o mayores.

No continúes si el resultado es `REJECTED` o si existen observaciones críticas o
mayores. Corrige el borrador y repite la auditoría.

Para continuar después de una auditoría aprobada, usa el comando que Antigravity
muestre en `/help`, conceptualmente:

```text
/approve-spec sprint_05_seasonality
```

La aprobación solo es válida si `spec.md` existe, la auditoría indica
`STATUS: APPROVED` y no hay observaciones críticas o mayores.

### Paso C: diseño técnico

Solo con `spec.md` aprobado:

> Diseña el TDD de `specs/sprint_05_seasonality/spec.md`. Genera
> `specs/sprint_05_seasonality/plan.md` con módulos afectados, dataclasses o
> Pydantic, firmas tipadas, excepciones, validaciones, diagrama Mermaid y casos
> de prueba. No modifiques `spec.md`.

### Paso D: implementación

> Implementa únicamente lo definido en
> `specs/sprint_05_seasonality/plan.md`. Modifica `src/` y crea las pruebas
> necesarias en `tests/`. Usa inyección de dependencias, PEP 484, docstrings,
> configuración externa y SKU `MODELO-TALLA-COLOR`. No cambies specs aprobadas.

### Paso E: QA

> Ejecuta el loop QA sobre el incremento. Reporta archivo, línea, causa y
> corrección para cada fallo. Verifica Pylint >= 7.0, cobertura >= 80%, F1 >=
> 0.80 cuando aplique y regresión E2E. Genera `logs/qa_report.json` con
> resultados, comandos, versión del entorno y estado de cada quality gate.

### Paso F: empaquetado

> Ejecuta la validación final y actualiza solo los artefactos de DevOps
> permitidos: `requirements.txt`, `run.sh`, README y métricas. Conserva
> separadas las métricas históricas del benchmark agéntico y las métricas del
> pipeline de inventario.

## 5. Benchmark baseline vs. optimizado

El objetivo no es reducir tokens a cualquier costo. La variante optimizada solo
se acepta si conserva o mejora calidad funcional, técnica y analítica.

### 5.1 Preparar dos ejecuciones

Ejecuta exactamente las mismas tareas con:

- **Baseline:** contratos/contexto usados antes de la política de carga
  progresiva.
- **Optimizado:** contratos actuales, activación selectiva y handoffs mínimos.

No cambies al mismo tiempo el modelo, la temperatura, los datos, los criterios
de aceptación ni el tamaño de la tarea.

### 5.2 Tareas A1-A6

Usa las tareas definidas en `docs/agent_efficiency_benchmark.md`:

```text
A1: necesidad -> SRS EARS
A2: SRS -> diseño técnico
A3: regla de inventario -> implementación y pruebas
A4: fallo reproducible -> diagnóstico y parche
A5: dataset -> análisis estadístico reproducible
A6: datos comerciales -> recomendación con regla de decisión
```

Para cada tarea, guarda el resultado fuera del repositorio si contiene
información sensible y registra solo el resumen cuantitativo. Cada registro debe
contener como mínimo:

```json
{
  "benchmark_version": "1.0",
  "variant": "baseline",
  "task_id": "A1",
  "skills_loaded": ["product_analysis"],
  "input_tokens": 0,
  "output_tokens": 0,
  "tool_calls": 0,
  "retries": 0,
  "latency_seconds": 0.0,
  "quality_score": 0.0,
  "defects": [],
  "accepted": false
}
```

Si Antigravity no expone tokens o costo, marca esos campos como `null` y no
inventes valores. En ese caso, la comparación puede medir calidad, llamadas,
reintentos y latencia, pero debe declararse incompleta para tokens/costo.

### 5.3 Criterios de aceptación

Acepta el arnés optimizado únicamente si:

1. No introduce defectos críticos.
2. Cumple los mismos criterios de aceptación que el baseline.
3. No reduce cobertura, Pylint, F1 ni reproducibilidad.
4. Reduce tokens, llamadas, reintentos o latencia, o demuestra una mejora
   equivalente con evidencia.
5. Conserva trazabilidad de skills, prompts/versiones y artefactos.

## 6. Comandos de validación posterior

Después de cada cambio:

```bash
PYTHONPATH=. pytest --cov=src --cov-report=term-missing tests/
python3 -m pylint src/
./run.sh
```

Valida también los contratos del arnés:

```bash
PYTHONPATH=. pytest tests/test_agent_harness.py -q
```

Antes de entregar resultados:

```bash
git diff --check
git status --short
```

## 7. Artefactos que deben existir al cerrar una iteración

```text
specs/sprint_XX/spec_draft.md
specs/sprint_XX/audit_report.md
specs/sprint_XX/spec.md
specs/sprint_XX/plan.md
logs/qa_report.json
logs/execution_metrics.json
logs/executive_report.md
```

Los artefactos que no apliquen deben declararse como `N/A` con una justificación
en el reporte, no omitirse silenciosamente.

## 8. Diagnóstico de fallos frecuentes

| Síntoma | Acción |
|---|---|
| `spec.md` se crea sin aprobación | Detener el pipeline y volver a Fase A |
| Skill no encontrada | Revisar `activation`, ruta `.agents/skills` y referencia JSON |
| Tokens no disponibles | Registrar `null`; no estimar manualmente como métrica oficial |
| Falla de cobertura | Añadir pruebas de comportamiento, no tests triviales |
| Falla de F1 | Revisar etiquetas, dataset, leakage, umbrales y casos frontera |
| Falla E2E | Ejecutar primero `pytest` y luego `python3 src/main.py` con el dataset |
| API Gemini no disponible | Usar el fallback determinista y registrar el modo offline |

## 9. Orden exacto para la próxima sesión

1. Ejecutar `./run.sh`.
2. Elegir una sola tarea A1-A6.
3. Ejecutarla en modo baseline y guardar sus métricas.
4. Ejecutarla con las skills selectivas actuales.
5. Comparar calidad antes de comparar tokens.
6. Registrar el resultado en el formato del benchmark.
7. Repetir hasta cubrir A1-A6.
8. Solo después consolidar conclusiones para la tesis.

## 10. Prueba propuesta: convertir Word a Markdown

Para probar una solicitud distinta al caso de inventario, usa una conversación
directa con el Coordinator. Esta prueba debe crear primero una especificación,
no modificar el documento original ni implementar código de inmediato.

```text
Necesito diseñar un algoritmo y luego implementarlo para convertir un archivo
Microsoft Word DOCX a Markdown.

Entrada:
- archivo: SDLC-AI_Tesis_Entrega1.docx
- salida esperada: docs/SDLC-AI_Tesis_Entrega1_convertida.md

Requisitos:
1. Preservar títulos, subtítulos, párrafos, listas, tablas, referencias,
   caracteres UTF-8 y el orden del contenido.
2. Definir qué hacer con imágenes, notas, encabezados, pies y formato que
   Markdown no soporte.
3. No sobrescribir el DOCX original.
4. No inventar ni resumir contenido.
5. Generar un reporte de advertencias y validación de conteos.
6. Proponer primero la especificación; no escribir código hasta mi aprobación
   de spec.md.

Activa únicamente document_conversion y python_architect.
```

El resultado correcto de la primera interacción es:

```text
docx_to_markdown/specs/sprint_01_conversion/spec_draft.md
docx_to_markdown/specs/sprint_01_conversion/audit_report.md
estado: WAITING_APPROVAL
```

Después de aprobar `spec.md`, el Coordinator debe continuar con `plan.md`,
implementación, pruebas y QA. Para la primera prueba conviene usar un DOCX
pequeño de fixture; deja la tesis completa para la validación final.
