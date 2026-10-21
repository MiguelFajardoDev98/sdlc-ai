---
name: big_data
description: Diseña pipelines escalables de datos con costos, particiones y fallos explícitos.
activation: volumen, velocidad, distribución, streaming, batch o procesamiento paralelo.
---

# Big data

## Procedimiento
1. Cuantificar volumen, crecimiento, latencia, concurrencia y retención.
2. Elegir batch/streaming, almacenamiento, particionamiento y formato.
3. Definir idempotencia, checkpoints, reintentos, observabilidad y backpressure.
4. Estimar costo y probar con datos representativos; evitar escalar por intuición.
5. Entregar esquema, flujo, SLOs, límites y plan de recuperación.

## Guardrails
No distribuir un problema pequeño sin evidencia, no ignorar skew, duplicados,
orden de eventos, evolución de esquema o datos sensibles.

## Salida
`workload`, `architecture`, `data_contract`, `failure_modes`, `slo`,
`cost_model` y `test_plan`.
