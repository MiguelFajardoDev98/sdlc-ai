# ESPECIFICACIÓN DE REQUISITOS DE SOFTWARE APROBADA (SRS v1.0 INMUTABLE) — SPRINT 01

- **Proyecto:** Caso de Estudio `todo_list` (SDLC-AI)
- **Sprint:** 01 — Aplicación de Lista de Tareas con Grafo de Dependencias, Persistencia JSON y Dashboard Web
- **Estado:** **APROBADO (v1.0 INMUTABLE)** — Auditado en `specs/sprint_01/audit_report.md`
- **Dictamen de Auditoría:** `DICTAMEN: APROBADO SIN OBSERVACIONES CRÍTICAS O MAYORES`
- **Puerto HTTP por Defecto:** `8082`
- **Restricción de Entorno:** Librería estándar de Python (`stdlib`) exclusivamente para `src/todo_list/`.

---

## 1. HISTORIAS DE USUARIO Y TRAZABILIDAD

| ID | Historia de Usuario | Requisitos EARS Asociados | Criterios de Aceptación | Puntos de Historia (PH) |
| :--- | :--- | :--- | :--- | :---: |
| `HU-01` | Gestión CRUD completa de tareas con validación de prioridad, estado, fecha límite (`YYYY-MM-DD`) y etiquetas. | `REQ-01`, `REQ-02`, `REQ-03` | `CA-01` | 5 |
| `HU-02` | Gestión de dependencias entre tareas, detección de ciclos (DFS/BFS) y bloqueo de completado ante tareas previas pendientes/en progreso. | `REQ-04`, `REQ-05`, `REQ-06` | `CA-02`, `CA-03` | 8 |
| `HU-03` | Filtrado combinable por estado, prioridad, etiqueta y vencimiento, más búsqueda textual. | `REQ-07` | `CA-01` | 3 |
| `HU-04` | Resumen estadístico en tiempo real incluyendo conteo de tareas vencidas, bloqueadas y porcentaje de avance. | `REQ-08` | `CA-04` | 3 |
| `HU-05` | Persistencia local en archivo JSON con tolerancia y respaldo automático ante corrupción o archivo vacío. | `REQ-09`, `REQ-10` | `CA-05` | 3 |
| `HU-06` | Servidor HTTP REST JSON y Dashboard Web moderno en español en `localhost:8082`. | `REQ-11`, `REQ-12` | `CA-01`..`CA-05` | 5 |

---

## 2. REQUISITOS FUNCIONALES Y NO FUNCIONALES (EARS)

### REQ-01 (Ubiquitous): Modelo de Dominio y Validaciones
El sistema **deberá** modelar cada tarea (`Task`) con los siguientes campos validados:
- `id` (`str`): Identificador único (UUID4 por defecto, cadena no vacía).
- `title` (`str`): Título obligatorio (1 a 200 caracteres tras eliminar espacios iniciales/finales).
- `description` (`str`): Descripción opcional (cadena vacía `""` por defecto).
- `priority` (`Priority`): Enumeración con valores `"baja"`, `"media"` (por defecto), `"alta"`.
- `status` (`TaskStatus`): Enumeración con valores `"pendiente"` (por defecto), `"en_progreso"`, `"completada"`.
- `due_date` (`Optional[str]`): Fecha opcional en formato estricto `YYYY-MM-DD` validada con `datetime.date.fromisoformat`, o `None`.
- `tags` (`List[str]`): Lista de etiquetas normalizadas (minúsculas, sin espacios vacíos, preservando orden sin duplicados).
- `dependencies` (`List[str]`): Lista de IDs de tareas previas requeridas (sin duplicados, preservando orden).
- `created_at` (`str`) y `updated_at` (`str`): Timestamps ISO-8601.

### REQ-02 (Event-Driven): Operaciones CRUD
**Cuando** se invoque la creación, lectura, actualización o eliminación de una tarea, el sistema **deberá** validar las invariantes de dominio, persistir el estado actualizado en el archivo JSON y retornar la entidad o lanzar una excepción específica de dominio.

### REQ-03 (Event-Driven): Integridad Referencial al Eliminar
**Cuando** se elimine una tarea existente, el sistema **deberá** remover su `id` de la lista `dependencies` de todas las demás tareas registradas antes de guardar en disco.

### REQ-04 (Unwanted Behaviour): Validación de Dependencias Existentes y No Reflexivas
**Si** se especifica como dependencia el propio `id` de la tarea o un `id` inexistente en el repositorio, el sistema **deberá** rechazar la operación lanzando `InvalidDependencyError` (subclase de `ValidationError`).

### REQ-05 (Unwanted Behaviour): Detección de Dependencias Circulares
**Si** al crear o actualizar una tarea sus dependencias generan un ciclo directo o indirecto en el grafo de tareas ($u \to \dots \to u$), el sistema **deberá** detectarlo mediante recorrido DFS/BFS y abortar la operación lanzando `CyclicDependencyError` con la traza del ciclo detectado.

### REQ-06 (State-Driven / Unwanted Behaviour): Bloqueo de Completado por Dependencias Incompletas
**Mientras** una tarea tenga al menos una dependencia cuyo estado no sea `"completada"`, **si** se intenta establecer su estado en `"completada"`, el sistema **deberá** impedir la operación lanzando `DependencyNotCompletedError` con la lista de tareas previas pendientes o en progreso.
Además, **si** una tarea que ya está `"completada"` pretende reabrirse a `"pendiente"` o `"en_progreso"` mientras otra tarea dependiente de ella ya está `"completada"`, el sistema **deberá** rechazar el cambio o validar la consistencia para no dejar tareas completadas con dependencias incompletas.

### REQ-07 (Event-Driven): Filtros y Búsqueda por Texto
**Cuando** se listen tareas indicando filtros opcionales (`status`, `priority`, `tag`, `search`, `overdue_only`), el sistema **deberá** aplicar conjunción lógica (`AND`) de los criterios suministrados y evaluar `search` de forma case-insensitive sobre `title`, `description` y `tags`.

### REQ-08 (State-Driven): Tareas Vencidas y Resumen Estadístico
**Mientras** se evalúe el estado del tablero en relación con una fecha de referencia (`reference_date`, por defecto `date.today()`), el sistema **deberá** clasificar una tarea como vencida (`is_overdue = True`) si `due_date is not None`, `date.fromisoformat(due_date) < reference_date` y `status != "completada"`. El método de resumen estadístico **deberá** retornar:
- `total`: Número total de tareas.
- `by_status`: `{"pendiente": int, "en_progreso": int, "completada": int}`.
- `by_priority`: `{"baja": int, "media": int, "alta": int}`.
- `overdue_count`: Conteo de tareas vencidas.
- `blocked_count`: Conteo de tareas no completadas con al menos una dependencia no completada.
- `completion_rate`: Porcentaje `float` (`0.0` si `total == 0`, o `round((completadas / total) * 100, 2)`).

### REQ-09 (Ubiquitous): Persistencia JSON Segura
El sistema **deberá** persistir la colección de tareas en formato JSON indentado en UTF-8 mediante escritura segura en archivo temporal y reemplazo atómico (`os.replace`).

### REQ-10 (Unwanted Behaviour): Recuperación ante Archivo Corrupto o Vacío
**Si** el archivo JSON está vacío o contiene JSON malformado o estructura no válida, el sistema **deberá** respaldar el archivo dañado en `<archivo>.corrupt` y re-inicializar el almacenamiento como `[]` sin interrumpir la ejecución.

### REQ-11 (Event-Driven): Servidor Web y API REST JSON
**Cuando** se reciba una solicitud HTTP en el servidor (`wsgiref` / `http.server`), el sistema **deberá** servir los recursos estáticos (`/` -> `index.html`, `/static/*`) y los endpoints REST JSON:
- `GET /api/tasks`: Lista tareas enriquecidas con metadatos calculados (`is_overdue`, `is_blocked`, `blocking_dependencies`, `dependency_titles`), soportando query params `status`, `priority`, `tag`, `search`, `overdue_only`.
- `POST /api/tasks`: Crea una tarea (`201 Created`).
- `GET /api/tasks/<id>`: Obtiene detalle de una tarea (`200 OK` o `404 Not Found`).
- `PUT /api/tasks/<id>`: Actualiza integral o parcialmente una tarea (`200 OK`).
- `PATCH /api/tasks/<id>/status`: Cambia el estado de una tarea (`200 OK` o `409 Conflict` si está bloqueada).
- `DELETE /api/tasks/<id>`: Elimina una tarea y limpia dependencias (`200 OK`).
- `GET /api/summary`: Retorna el resumen estadístico (`200 OK`).

### REQ-12 (Ubiquitous): Dashboard Web Moderno en Español
El sistema **deberá** ofrecer una interfaz gráfica Web responsiva en español (puerto por defecto `8082`) con tarjetas KPI de resumen (total, pendientes, en progreso, completadas, vencidas, bloqueadas), barra de progreso, controles de búsqueda y filtrado, formulario modal/lateral con selector interactivo de dependencias existentes, insignias visuales de prioridad/estado/vencimiento/bloqueo y notificaciones claras de error o éxito.

---

## 3. CRITERIOS DE ACEPTACIÓN Y QUALITY GATES

1. **CA-01 (CRUD y Validaciones):** Creación, edición, lectura y borrado de tareas validando campos obligatorios, enumeraciones y fechas `YYYY-MM-DD`.
2. **CA-02 (Grafo Acíclico):** Rechazo determinista de auto-dependencias y ciclos de longitud $k \ge 1$ mediante DFS/BFS.
3. **CA-03 (Bloqueo por Dependencias):** Rechazo de completado cuando existan dependencias no completadas, informando los títulos/IDs bloqueantes.
4. **CA-04 (Vencimientos y KPIs):** Cálculo exacto de `overdue_count`, `blocked_count`, `completion_rate` y desgloses por estado y prioridad.
5. **CA-05 (Resiliencia JSON):** Recuperación limpia ante archivos JSON vacíos o corruptos.
6. **Quality Gates SDLC-AI:** Cobertura de pruebas `>= 85%` con `pytest-cov` y calificación `10.00/10` en `pylint`.
