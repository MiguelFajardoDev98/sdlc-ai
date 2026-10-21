# Benchmark de eficiencia y calidad agéntica

## Propósito

Comparar el arnés vigente con una versión optimizada sin confundir ahorro de
tokens con calidad. Cada variante debe ejecutar las mismas tareas, entradas,
modelo, límites y criterios de evaluación.

## Tareas mínimas

| ID | Tarea | Evidencia principal |
|---|---|---|
| A1 | Convertir una necesidad en SRS EARS | completitud, ambigüedades, criterios testeables |
| A2 | Diseñar un módulo Python | contratos, tipos, excepciones, diagrama |
| A3 | Implementar una regla de inventario | pruebas, edge cases, calidad estática |
| A4 | Diagnosticar un fallo | causa raíz, parche, regresión |
| A5 | Analizar un dataset | fórmula, validación, incertidumbre, limitaciones |
| A6 | Recomendar una decisión comercial | evidencia, impacto, riesgo, regla de decisión |

## Métricas

- **Calidad funcional:** requisitos satisfechos / requisitos evaluables.
- **Defectos:** errores críticos, mayores y menores encontrados por revisión
  independiente.
- **Calidad técnica:** pruebas, cobertura, Pylint, tipado y reproducibilidad.
- **Calidad analítica:** exactitud de fórmulas, F1 cuando aplique, leakage,
  supuestos y análisis de error.
- **Eficiencia:** tokens de entrada/salida, llamadas, reintentos, latencia y
  costo por tarea.
- **Retrabajo:** cambios posteriores, fallos de validación y tiempo hasta
  obtener un artefacto aceptado.

## Criterio de no-regresión

La variante optimizada solo se acepta si mantiene o mejora la calidad funcional,
técnica y analítica del baseline. El ahorro de tokens se reporta por separado y
no compensa un defecto crítico, una regresión de cobertura, una métrica
incorrecta o una pérdida de trazabilidad.

## Registro reproducible

Cada ejecución debe guardar un registro versionado con:

```json
{
  "benchmark_version": "1.0",
  "variant": "baseline|optimized",
  "task_id": "A1",
  "input_hash": "sha256:...",
  "skills_loaded": [],
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

Los resultados deben conservar la versión de prompts, skills y criterios usada.
No se deben mezclar con las métricas de ejecución del pipeline de inventario:
son dimensiones experimentales distintas.
