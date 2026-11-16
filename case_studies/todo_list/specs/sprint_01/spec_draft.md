# BORRADOR DE ESPECIFICACIÓN DE REQUISITOS (SRS DRAFT) — SPRINT 01: GESTOR DE TAREAS (TO-DO LIST)

- **Proyecto:** Caso de Estudio `todo_list` (SDLC-AI)
- **Sprint:** 01 — Núcleo de Dominio, Grafo de Dependencias, Persistencia JSON y Dashboard Web
- **Agente Autor:** `Analyst_Agent` (Fase A — Análisis y Elicitación)
- **Sintaxis de Requisitos:** EARS (Easy Approach to Requirements Syntax) y Gherkin
- **Restricción Tecnológica:** Librería estándar de Python 3 (`stdlib` exclusivamente en producción) + HTML5/CSS3/JS Vanilla en español (puerto por defecto `8082`).

---

## 1. HISTORIAS DE USUARIO

| ID | Historia de Usuario | Requisitos EARS Asociados | Puntos de Historia (PH) |
| :--- | :--- | :--- | :---: |
| `HU-01` | **Como** usuario, **quiero** crear, consultar, actualizar y eliminar tareas con título, descripción opcional, prioridad (`baja`, `media`, `alta`), estado (`pendiente`, `en_progreso`, `completada`), fecha límite (`YYYY-MM-DD`) y etiquetas, **para** organizar mis actividades. | `REQ-01`, `REQ-02`, `REQ-03` | 5 |
| `HU-02` | **Como** usuario, **quiero** definir dependencias entre tareas existentes y que el sistema impida ciclos y bloquee el completado si existen dependencias previas sin completar, **para** garantizar el orden lógico de ejecución. | `REQ-04`, `REQ-05`, `REQ-06` | 8 |
| `HU-03` | **Como** usuario, **quiero** filtrar tareas por estado, prioridad, etiqueta o vencimiento y buscarlas por texto libre en título, descripción o etiquetas, **para** localizar rápidamente elementos relevantes. | `REQ-07` | 3 |
| `HU-04` | **Como** usuario, **quiero** visualizar un resumen estadístico que incluya el total de tareas, desglose por estado, desglose por prioridad, tasa de completitud y conteo de tareas vencidas, **para** monitorear mi progreso. | `REQ-08` | 3 |
| `HU-05` | **Como** usuario, **quiero** que todas las tareas persistan automáticamente en un archivo JSON local con recuperación tolerante a archivos vacíos o corruptos, **para** conservar mis datos entre sesiones sin motores externos. | `REQ-09`, `REQ-10` | 3 |
| `HU-06` | **Como** usuario, **quiero** interactuar con la aplicación mediante una API REST JSON y un panel visual Web moderno en español servido en `localhost:8082`, **para** gestionar las tareas de forma intuitiva desde cualquier navegador. | `REQ-11`, `REQ-12` | 5 |

---

## 2. ESPECIFICACIÓN DE REQUISITOS DEL SISTEMA (FORMATO EARS)

### REQ-01 (Ubiquitous): Modelo de Datos y Validaciones de Dominio
El sistema **deberá** representar cada tarea con los siguientes atributos tipados y validados:
- `id`: Identificador único en cadena (UUID4 o slug único no vacío).
- `title`: Cadena obligatoria no vacía (tras `strip()`), longitud entre 1 y 200 caracteres.
- `description`: Cadena opcional (por defecto `""`).
- `priority`: Enumeración estricta con valores `{"baja", "media", "alta"}` (por defecto `"media"`).
- `status`: Enumeración estricta con valores `{"pendiente", "en_progreso", "completada"}` (por defecto `"pendiente"`).
- `due_date`: Fecha límite opcional en formato ISO estricto `YYYY-MM-DD` válido en calendario, o `None`.
- `tags`: Lista de cadenas normalizadas (en minúsculas, sin espacios extremos ni duplicados).
- `dependencies`: Lista de identificadores (`id`) de tareas existentes de las cuales depende la tarea actual (sin duplicados).
- `created_at` y `updated_at`: Marcas de tiempo en formato ISO-8601.

### REQ-02 (Event-Driven): Operaciones CRUD de Tareas
**Cuando** se solicite crear, obtener, actualizar o eliminar una tarea, el sistema **deberá** validar sus atributos, sincronizar el cambio en el repositorio JSON y retornar la entidad resultante (o lanzar una excepción de dominio tipada si el identificador no existe o los datos son inválidos).

### REQ-03 (Event-Driven): Limpieza de Referencias al Eliminar
**Cuando** una tarea sea eliminada del sistema, el sistema **deberá** remover automáticamente su `id` de la lista `dependencies` de cualquier otra tarea que dependiera de ella, manteniendo la integridad referencial del grafo.

### REQ-04 (Unwanted Behaviour): Validación de Existencia y Auto-Dependencia
**Si** una tarea intenta declarar como dependencia su propio `id` (auto-dependencia) o un `id` que no existe en el repositorio, el sistema **deberá** rechazar la operación lanzando una excepción de validación descriptiva.

### REQ-05 (Unwanted Behaviour): Prevención de Dependencias Circulares (Detección de Ciclos)
**Si** la adición o actualización de dependencias entre tareas introduce un ciclo directo o indirecto en el grafo dirigido ($A \to B \to \dots \to A$), el sistema **deberá** detectar el ciclo mediante recorrido de grafos (DFS/BFS) y rechazar la operación antes de persistir cambios.

### REQ-06 (State-Driven / Unwanted Behaviour): Bloqueo de Completado por Dependencias Incompletas
**Mientras** una tarea posea al menos una tarea dependencia cuyo estado sea distinto de `"completada"`, **si** se intenta cambiar el estado de la tarea dependiente a `"completada"`, el sistema **deberá** bloquear la transición y lanzar un error de negocio indicando explícitamente cuáles tareas previas faltan por completar.

### REQ-07 (Event-Driven): Filtrado Multicriterio y Búsqueda por Texto
**Cuando** se consulten las tareas con parámetros de filtro (`status`, `priority`, `tag`, `search`, `overdue_only`), el sistema **deberá** retornar únicamente las tareas que satisfagan simultáneamente (conjunción lógica `AND`) todos los filtros activos, buscando la cadena `search` de forma insensible a mayúsculas/minúsculas en `title`, `description` y `tags`.

### REQ-08 (State-Driven): Cómputo de Tareas Vencidas y Resumen Estadístico
**Mientras** existan tareas registradas en el sistema, el sistema **deberá** considerar una tarea como **vencida** (`is_overdue = True`) si y solo si posee `due_date` definida, `due_date < fecha_actual_referencia` (`date.today()`) y `status != "completada"`. El resumen estadístico **deberá** exponer:
- `total`: Total de tareas.
- `by_status`: Conteo para `"pendiente"`, `"en_progreso"` y `"completada"`.
- `by_priority`: Conteo para `"baja"`, `"media"` y `"alta"`.
- `overdue_count`: Conteo de tareas vencidas no completadas.
- `blocked_count`: Conteo de tareas no completadas que tienen al menos una dependencia sin completar.
- `completion_rate`: Porcentaje de tareas completadas sobre el total (`0.0` a `100.0`, redondeado a 2 decimales).

### REQ-09 (Ubiquitous): Persistencia en Archivo JSON Atómica y Segura
El sistema **deberá** almacenar las tareas en un archivo JSON codificado en UTF-8 utilizando escritura segura y creando automáticamente los directorios padres si no existen.

### REQ-10 (Unwanted Behaviour): Tolerancia a Persistencia Corrupta o Vacía
**Si** el archivo JSON de persistencia no existe, está vacío (0 bytes) o contiene sintaxis JSON corrupta/estructura inválida, el sistema **deberá** respaldar el archivo corrupto (con sufijo `.corrupt`), inicializar el estado como una colección vacía `[]` sin colapsar la aplicación y registrar la recuperación.

### REQ-11 (Event-Driven): API HTTP REST JSON
**Cuando** el servidor HTTP reciba peticiones en `/api/tasks` y `/api/summary`, el sistema **deberá** procesar endpoints REST (`GET /api/tasks`, `POST /api/tasks`, `GET /api/tasks/<id>`, `PUT /api/tasks/<id>`, `PATCH /api/tasks/<id>/status`, `DELETE /api/tasks/<id>`, `GET /api/summary`) devolviendo respuestas JSON con códigos HTTP semánticos (`200`, `201`, `400`, `404`, `409`, `500`) y mensajes de error en español.

### REQ-12 (Ubiquitous): Interfaz Gráfica Web en Español (Puerto 8082)
El sistema **deberá** servir en `http://localhost:8082` (configurable por CLI/entorno) una aplicación Web responsiva en español que permita visualizar tarjetas KPI (incluyendo tareas vencidas), crear y editar tareas con selector de dependencias, filtrar por estado/prioridad, buscar en tiempo real, cambiar estados/completar tareas mostrando alertas claras ante bloqueos por dependencias o ciclos, y eliminar tareas.

---

## 3. CRITERIOS DE ACEPTACIÓN VERIFICABLES (GHERKIN)

1. **Creación y Validación (`CA-01`):**
   - `GIVEN` un payload con título `"Preparar informe"`, prioridad `"alta"`, fecha `"2026-12-31"` y etiquetas `["tesis", "urgente"]`
   - `WHEN` se crea la tarea
   - `THEN` se persiste en JSON con estado `"pendiente"`, ID único y se recupera intacta.
2. **Detección de Ciclos (`CA-02`):**
   - `GIVEN` tres tareas `T1`, `T2`, `T3` donde `T2` depende de `T1` y `T3` depende de `T2`
   - `WHEN` se intenta actualizar `T1` para que dependa de `T3`
   - `THEN` el sistema rechaza la operación con error de dependencia circular (`CyclicDependencyError` / HTTP `409`) y el grafo permanece sin ciclos.
3. **Bloqueo de Completado (`CA-03`):**
   - `GIVEN` una tarea `T2` que depende de `T1` y `T1` está en estado `"pendiente"`
   - `WHEN` se intenta marcar `T2` como `"completada"`
   - `THEN` el sistema bloquea el cambio con error de dependencia incompleta (`DependencyNotCompletedError` / HTTP `409`) indicando que `T1` no está completada.
4. **Cálculo de Tareas Vencidas (`CA-04`):**
   - `GIVEN` una tarea con `due_date = "2020-01-01"` en estado `"pendiente"` y otra con la misma fecha en estado `"completada"`
   - `WHEN` se solicita el resumen estadístico
   - `THEN` `overdue_count` contabiliza únicamente la tarea no completada (`1`).
5. **Recuperación ante Archivo JSON Corrupto (`CA-05`):**
   - `GIVEN` un archivo JSON con contenido truncado `"{bad json"`
   - `WHEN` se inicializa el repositorio
   - `THEN` el sistema crea una copia de respaldo `.corrupt`, inicializa la lista vacía sin lanzar excepción fatal y permite operar normalmente.
