# Informe de Benchmark Empírico: Desarrollo en Línea Base (Sin Arnés) vs. Marco SDLC-AI

**Caso de Estudio Experimental:** Aplicación Web Local de Gestión de Tareas (*To-Do List*) con Grafo de Dependencias y Persistencia JSON.  
**Fecha de Ejecución:** 15 de noviembre de 2026  

---

## 1. Enlaces Directos a las Sesiones y Evidencias

| Sesión | Enlace Interactivo Antigravity | Bitácora Exportada (Markdown) | Directorio de Código | Interfaz Gráfica Web Local |
| :--- | :--- | :--- | :--- | :--- |
| **Sesión A (Línea Base / Sin Arnés)** | [Abrir Sesión A](conversation://3876d820-f32e-45f5-a376-78f8c376c442) | [transcript_sesion_a.md](file:///home/admin/Projects/Academico/2026-02/TrabajoDeGrado/SDLC-AI/benchmarks/todo_list/sesion_a_baseline/transcript_sesion_a.md) | `benchmarks/todo_list/sesion_a_baseline/` | `http://localhost:8081` |
| **Sesión B (Marco SDLC-AI)** | [Abrir Sesión B](conversation://286ff638-251c-4dea-b35c-164ef3975010) | [transcript_sesion_b.md](file:///home/admin/Projects/Academico/2026-02/TrabajoDeGrado/SDLC-AI/case_studies/todo_list/transcript_sesion_b.md) | `case_studies/todo_list/` | `http://localhost:8082` |

---

## 2. Tabla Comparativa de Resultados Cuantitativos

Ambas sesiones recibieron **exactamente el mismo prompt en lenguaje natural** y fueron evaluadas con las mismas herramientas de auditoría (`pylint`, `pytest-cov` y la batería externa ciega de 10 pruebas `blind_chaos_suite.py`):

| Dimensión / Métrica | Sesión A: Línea Base (Sin Arnés) | Sesión B: Marco SDLC-AI (Con Arnés) | Diferencia / Impacto ($\Delta$) |
| :--- | :---: | :---: | :--- |
| **Tiempo de Ejecución ($T_{gen}$)** | `474.0 s` (7m 54s) | `901.0 s` (15m 01s) | $+427.0\text{ s}$ (Inversión en Especificación, Diseño y QA) |
| **Pasos de Razonamiento (`planner_steps`)** | `14` | `27` | $+92.8\%$ profundidad analítica |
| **Llamadas a Herramientas (`tool_calls`)** | `13` | `47` | Incluye bucle cerrado de verificación (`Tester_Agent`) |
| **Artefactos de Ingeniería (SRS/Diseño/QA)** | `0` (Solo `README.md`) | `5` (`spec_draft.md`, `audit_report.md`, `spec.md`, `plan.md`, `qa_report.json`) | **Trazabilidad formal completa (EARS + Gherkin + Mermaid)** |
| **Calificación Estática (`Pylint`)** | **`8.92 / 10.00`** | **`10.00 / 10.00`** | **$+1.08$ puntos** ($0$ violaciones vs. $69$ advertencias) |
| **Violaciones/Advertencias de Código** | `69` | `0` | **$-100\%$ de deuda técnica estática** |
| **Cobertura Total de Pruebas (`pytest-cov`)** | **`75.0%`** (`app.py`: `55%`) | **`97.0%`** (`web.py`: `95%`, `service.py`: `99%`) | **$+22.0$ puntos porcentuales de cobertura** |
| **Velocidad de Suite Unitaria** | `0.70 s` (6 tests) | `0.17 s` (11 tests) | **$4.1\times$ más rápida** (gracias a diseño WSGI desacoplado) |
| **Batería Ciega Funcional (Happy Path)** | `5 / 5` (`100%`) | `5 / 5` (`100%`) | Empate en funcionalidad básica |
| **Batería Ciega de Caos y Frontera** | **`2 / 5` (`40%`)** | **`5 / 5` (`100%`)** | **$+60\%$ de resiliencia ante fallos y casos extremos** |
| **Puntaje Total Batería Ciega (10 casos)** | **`7 / 10` (`70%`)** | **`10 / 10` (`100%`)** | **$+30\%$ de efectividad global** |
| **Dictamen de Compuerta de Producción** | ❌ **RECHAZADO** | ✅ **CERTIFICADO** | Cero retrabajo humano requerido en Sesión B |

---

## 3. Hallazgos Críticos para la Discusión de la Tesis

### Hallazgo 1: El fenómeno de "Intención No Implementada" en LLMs sin Arnés (Caso `TC-09`)
Uno de los hallazgos empíricos más reveladores del experimento ocurrió en [gestor_tareas.py](file:///home/admin/Projects/Academico/2026-02/TrabajoDeGrado/SDLC-AI/benchmarks/todo_list/sesion_a_baseline/gestor_tareas.py#L375-L418) de la **Sesión A**. Al escribir el método `actualizar_tarea`, el modelo en modo libre redactó en su *docstring* (líneas 381-382):
```python
"""
- Que si tiene tareas dependientes ya completadas, no pueda reabrirse dejando inconsistencias
"""
```
Sin embargo, **en el cuerpo del método (líneas 384-417) olvidó por completo programar dicha validación**. Como resultado, si la Tarea B depende de la Tarea A y ambas están completadas, la Sesión A permite volver a poner la Tarea A como `pendiente`, corrompiendo la integridad lógica del grafo de tareas.

En contraste, en la **Sesión B (SDLC-AI)**, el `Auditor_Agent` convirtió esa condición en una regla formal auditable (`REQ-07` en [spec.md](file:///home/admin/Projects/Academico/2026-02/TrabajoDeGrado/SDLC-AI/case_studies/todo_list/specs/sprint_01/spec.md)), el `Architect_Agent` diseñó el método `_validate_dependents_consistency` en [service.py](file:///home/admin/Projects/Academico/2026-02/TrabajoDeGrado/SDLC-AI/case_studies/todo_list/src/todo_list/service.py#L168), y el `Tester_Agent` creó la prueba unitaria `test_service_completion_blocking_and_reopen_guard` en [test_todo_list.py](file:///home/admin/Projects/Academico/2026-02/TrabajoDeGrado/SDLC-AI/case_studies/todo_list/tests/test_todo_list.py).

### Hallazgo 2: Colapso ante Corrupción de Persistencia (`TC-08`)
- **Sesión A:** Si el archivo `tareas.json` sufre un truncamiento o corrupción en disco, `GestorTareas.cargar()` lanza un `RuntimeError` no controlado que impide que el servidor web arranque.
- **Sesión B (SDLC-AI):** Por exigencia de la auditoría de requisitos (`REQ-11`), `JsonTaskRepository` detecta el JSON malformado, crea automáticamente un respaldo `.corrupt` para análisis forense y reinicializa el almacén limpiamente sin derribar el servicio.

### Hallazgo 3: Deuda Técnica Invisible en el Servidor Web (`app.py` vs. `web.py`)
- En la **Sesión A**, el archivo `app.py` obtuvo apenas **55% de cobertura de pruebas** y concentró múltiples alertas de `pylint` (`broad-exception-caught`, `too-many-locals`, `too-many-return-statements`).
- En la **Sesión B**, `src/todo_list/web.py` fue diseñado como una aplicación WSGI pura y modular, alcanzando **95% de cobertura de pruebas** y **10.00/10 en Pylint**.

---

## 4. Cómo Inspeccionar Visualmente Ambas Aplicaciones Web

Para comparar ambas interfaces gráficas lado a lado en tu navegador **Firefox**:

```bash
# Terminal 1: Levantar Sesión A (Línea Base) en http://localhost:8081
python3 SDLC-AI/benchmarks/todo_list/sesion_a_baseline/app.py --port 8081

# Terminal 2: Levantar Sesión B (Marco SDLC-AI) en http://localhost:8082
PYTHONPATH=SDLC-AI/case_studies/todo_list/src python3 -m todo_list.web --port 8082
```
