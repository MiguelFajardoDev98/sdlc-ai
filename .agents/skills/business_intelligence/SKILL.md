---
name: business_intelligence
description: Modela datos, KPIs y visualizaciones trazables para decisiones de negocio.
activation: KPIs, dashboards, reporting, cubos, calidad de datos o análisis ejecutivo.
---

# Business intelligence

## Procedimiento
1. Declarar decisión, audiencia, granularidad, período y fuente.
2. Definir hechos, dimensiones, métricas, filtros y reglas de agregación.
3. Validar completitud, unicidad, consistencia temporal y unidad monetaria.
4. Diseñar visualización con contexto, umbrales, incertidumbre y drill-down.
5. Entregar diccionario de métricas y consultas reproducibles.

## Guardrails
Cada KPI debe tener fórmula, numerador, denominador, unidad, población, ventana
temporal y tratamiento de nulos. No mezclar niveles de granularidad ni confundir
correlación con causalidad.

## Salida
`decision`, `data_model`, `metric_dictionary`, `quality_checks`, `insights` y
`limitations`.
