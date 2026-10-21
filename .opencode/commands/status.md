---
description: Muestra el estado del pipeline SDLC-AI sin modificar archivos
agent: coordinator
---

Lee `ANTIGRAVITY.md`, `AGENTS.md`, `MEMORY.md` y los artefactos del task
indicado. Devuelve exclusivamente:

1. Estado actual.
2. Artefactos presentes y faltantes.
3. Skills activas.
4. Quality gates y último resultado.
5. Bloqueos.
6. Próxima acción permitida.

No escribas archivos ni ejecutes cambios de código.
