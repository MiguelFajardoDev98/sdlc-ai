# TECHNICAL DESIGN DOCUMENT (TDD) — SPRINT 4: DEVOPS Y EVALUACIÓN

- **Autor:** Agente Arquitecto (`Architect_Agent`)
- **Fase SDLC:** Fase B — Diseño Técnico

---

## 1. COMPONENTES Y ESTRUCTURA
- `requirements.txt`: Dependencias congeladas.
- `src/main.py`: Punto de entrada CLI para ejecución completa del pipeline.
- `run.sh`: Shell script automatizado con permisos de ejecución.
- `logs/execution_metrics.json`: Registro estructurado de telemetría, tiempos por fase y validación de la hipótesis $\Delta T \ge 30\%$.
- `README.md`: Documentación completa del proyecto para evaluación y despliegue rápido.
