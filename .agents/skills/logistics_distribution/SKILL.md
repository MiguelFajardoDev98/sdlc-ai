---
name: logistics_distribution
description: Optimiza inventario y distribución con demanda, lead time, capacidad y servicio.
activation: inventario, abastecimiento, transporte, bodegas, rutas, transferencias o retail.
---

# Logistics and distribution

## Procedimiento
1. Definir SKU, nodo, horizonte, demanda, lead time, capacidad y nivel de servicio.
2. Calcular cobertura, safety stock, fill rate, quiebre, rotación y costo total.
3. Incorporar estacionalidad, variabilidad, tallas/colores y restricciones regionales.
4. Comparar abastecimiento, transferencia y no intervención con reglas auditables.
5. Reportar recomendación, supuestos, sensibilidad, riesgo y plan de monitoreo.

## Guardrails
Respetar `MODELO-TALLA-COLOR`, unidades y fechas. No transferir por debajo del
stock de seguridad ni usar promedios que oculten tallas centrales o regiones.

## Salida
`network`, `demand`, `inventory_metrics`, `decision_rules`,
`recommendation`, `sensitivity` y `monitoring`.
