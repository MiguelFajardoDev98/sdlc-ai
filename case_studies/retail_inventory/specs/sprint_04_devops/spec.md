# ESPECIFICACIÓN DE REQUISITOS (SRS) — SPRINT 4: DEVOPS Y EMPAQUETADO

- **Sprint:** 04 — DevOps, Despliegue Portable y Evaluación Cuantitativa
- **Dominio:** Framework SDLC-AI
- **Sintaxis:** EARS (Easy Approach to Requirements Syntax)
- **Puntos de Historia del Sprint:** 6 PH (`HU-09`: 3 PH, `HU-10`: 2 PH, `HU-11`: 1 PH)

| Historia de Usuario | Requisitos EARS | Puntos de Historia (PH) |
|---|---|---:|
| `HU-09`: Integración del flujo principal por consola | `REQ-DEVOPS-03` | 3 |
| `HU-10`: Script de ejecución automática y validación de pruebas | `REQ-DEVOPS-01` | 2 |
| `HU-11`: Consolidación de tiempos de ejecución y métricas | `REQ-DEVOPS-02` | 1 |

---

## 1. REQUISITOS DE DEVOPS Y BENCHMARKING

### REQ-DEVOPS-01 (Ubiquitous): Portabilidad y Despliegue "One-Click"
El sistema **deberá** suministrar un script de ejecución multiplataforma (`run.sh`) que instale dependencias, ejecute la suite de verificación de calidad (Pytest y Pylint) y lance el pipeline completo sobre el dataset de validación sin configuración manual previa.

### REQ-DEVOPS-02 (State-Driven): Medición y Cálculo Empírico de $\Delta T$
**Mientras** se ejecuten las fases del SDLC, el sistema **deberá** registrar las marcas de tiempo (*timestamps*) por cada agente en `logs/execution_metrics.json` y calcular el porcentaje de reducción respecto a la línea base tradicional:
$$\Delta T (\%) = \left( \frac{E_{trad} - T_{SDLC-AI}}{E_{trad}} \right) \times 100$$
verificando el cumplimiento de la meta: $\Delta T \ge 30\%$.

### REQ-DEVOPS-03 (Event-Driven): Orquestación del Pipeline E2E
**Cuando** se invoque el comando principal (`src/main.py`), el framework **deberá** encadenar secuencialmente: Ingesta de datos -> Cómputo de KPIs -> Detección de Alertas y Transferencias -> Generación de Reporte Narrativo Ejecutivo (`logs/executive_report.md`).
