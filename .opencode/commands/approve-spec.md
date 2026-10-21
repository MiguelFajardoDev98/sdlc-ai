---
description: Aprueba una especificación y desbloquea el pipeline autónomo
agent: coordinator
---

Para el task `$ARGUMENTS`, verifica que exista `spec_draft.md`, que
`audit_report.md` tenga `STATUS: APPROVED` y que no existan observaciones
críticas o mayores.
Si alguna condición falla, informa el bloqueo y no modifiques archivos.
Si todas pasan, materializa `spec.md` desde `spec_draft.md`, marca la versión
aprobada, cambia el estado a `ARCHITECTING` y despacha Architect/Planner. No
sobrescribas un `spec.md` ya existente.
