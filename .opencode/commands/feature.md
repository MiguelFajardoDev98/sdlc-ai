---
description: Inicia una solicitud SDLC-AI desde el Coordinator sin tocar código
agent: coordinator
---
Quiero iniciar esta solicitud desde el Coordinator: $ARGUMENTS

Primero clasifica la solicitud, selecciona únicamente las skills pertinentes y
crea el task en el estado correcto. Si es una funcionalidad nueva, inicia la
Fase A. Crea únicamente `spec_draft.md` y `audit_report.md`; no crees
`spec.md`, `plan.md` ni código hasta la aprobación humana explícita.

Antes de escribir código, prepara un plan riguroso con:
1. Cómo la vas a implementar respetando las reglas de AGENTS.md y docs/constitution.md.
2. Formato de datos obligatorio para SKU: MODELO-TALLA-COLOR.
3. Qué archivos vas a modificar o crear y qué cambia en cada uno.
4. Casos límite, validaciones y pruebas requeridas (pylint >= 7.0, pytest-cov >= 80%, F1 >= 0.80).
5. Qué actualizarías en MEMORY.md.

No modifiques ningún archivo de código hasta que el plan esté aprobado.
