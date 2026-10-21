---
name: data_science
description: Resuelve problemas de datos con metodología reproducible y evaluación sin leakage.
activation: exploración, predicción, clasificación, experimentos o validación de modelos.
---

# Data science

## Procedimiento
1. Formular objetivo, variable objetivo, unidad de análisis y costo de error.
2. Auditar datos, sesgo, faltantes, duplicados, fuga y representatividad.
3. Separar train/validation/test respetando tiempo, grupos o entidades.
4. Establecer baseline, entrenar modelos simples antes de optimizar.
5. Reportar métricas, intervalos, calibración, errores por segmento y reproducibilidad.

## Guardrails
No usar información futura, no seleccionar por el conjunto de prueba, no declarar
causalidad desde predicción y no presentar una métrica sin su denominador.

## Salida
`problem`, `data_audit`, `baseline`, `method`, `metrics`, `error_analysis`,
`reproducibility` y `limitations`.
