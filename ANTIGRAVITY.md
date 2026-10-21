# Contrato operativo de Antigravity CLI 1.3.5

Este archivo define cómo debe comportarse el runtime cuando el investigador
conversa con el **Coordinator**. Los archivos de `.opencode/` describen los
roles y las skills; este contrato define el despacho, los artefactos y las
transiciones.

## Punto de entrada

Toda solicitud de desarrollo entra por `coordinator`. El usuario no debe
invocar directamente al implementador para una funcionalidad nueva.

El Coordinator debe:

1. Leer `AGENTS.md`, `docs/constitution.md` y `MEMORY.md`.
2. Clasificar la solicitud: especificación, corrección, análisis, QA o DevOps.
3. Activar solo las skills necesarias según `activation` en cada `SKILL.md`.
4. Crear o identificar el directorio `specs/sprint_XX_<slug>/`.
5. Mantener el estado en el artefacto de la fase y reportar el siguiente paso.

## Máquina de estados

```text
IDLE
  -> SPEC_DRAFTING       Analyst crea spec_draft.md
  -> SPEC_AUDITING       Auditor crea audit_report.md
  -> WAITING_APPROVAL    Coordinator espera aprobación humana del borrador
  -> SPEC_APPROVED       approve-spec materializa spec.md inmutable
  -> ARCHITECTING        Architect/Planner crea plan.md
  -> IMPLEMENTING        Developer/Implementer modifica src/ y tests/
  -> QA                  Tester/Reviewer ejecuta quality gates
  -> QA_REPAIR            Developer corrige; vuelve a QA, máximo 5 ciclos
  -> DEVOPS              DevOps actualiza empaquetado y métricas
  -> COMPLETED
```

Una observación crítica o mayor devuelve el flujo a `SPEC_DRAFTING`. Un fallo
de QA devuelve a `QA_REPAIR`; nunca se salta una puerta ni se modifica
`spec.md` aprobado.

## Handoff mínimo obligatorio

Cada agente recibe únicamente:

```yaml
task_id: sprint_XX_slug
state: CURRENT_STATE
objective: "resultado de esta fase"
input_artifacts:
  - "ruta/entrada"
constraints:
  - "restricción verificable"
active_skills:
  - "skill_name"
output_artifacts:
  - "ruta/salida"
acceptance_checks:
  - "comprobación"
```

El agente debe devolver:

```yaml
status: DONE | BLOCKED | REJECTED
artifacts:
  - path: "ruta/salida"
    status: created | updated | unchanged
checks:
  - name: "check"
    status: passed | failed | skipped
evidence: "comandos, líneas o resultado resumido"
next_state: "estado siguiente"
blockers: []
```

## Intervención humana

La única pausa normal ocurre después de `SPEC_AUDITING`, cuando el auditor
entrega un `audit_report.md` con `STATUS: APPROVED` y el borrador queda listo
para revisión. El Coordinator debe mostrar un resumen de cambios, supuestos y
riesgos y solicitar aprobación explícita. Antes de esa aprobación solo deben
existir `spec_draft.md` y `audit_report.md`; `spec.md` no debe crearse todavía.
Después de `/approve-spec`, el Coordinator materializa `spec.md` inmutable y
las fases de diseño, desarrollo, QA y DevOps son autónomas salvo bloqueo
técnico o fallo de calidad.

## Comandos conversacionales

Los nombres exactos de comandos deben registrarse en Antigravity usando `/help`.
La intención esperada es:

- `/feature <solicitud>`: iniciar una nueva solicitud desde el Coordinator.
- `/status`: mostrar estado, artefactos, bloqueos y quality gates.
- `/approve-spec <task_id>`: materializar y aprobar el `spec.md` indicado.
- `/reject-spec <task_id> <motivo>`: devolver a elicitación.
- `/qa <task_id>`: ejecutar o repetir QA.

Si el runtime no soporta comandos personalizados, el Coordinator debe aceptar
las mismas intenciones como texto natural.

## Smoke test

El smoke test debe usar una tarea que no modifique `src/`, por ejemplo:

> Crear una especificación para parametrizar el umbral de temporada navideña.
> No implementar código. Usar `retail_strategist`,
> `logistics_distribution` y `math_statistics`.

Se considera exitoso cuando:

1. Se crea `spec_draft.md`.
2. Se crea `audit_report.md`.
3. El estado queda en `WAITING_APPROVAL`.
4. No se crean `src/`, `tests/` ni `plan.md`.

Un segundo smoke test, después de aprobar la especificación, debe demostrar
`plan.md`, implementación, QA y estado final sin modificar la especificación
aprobada.
