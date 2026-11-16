# Lista de Tareas (To-Do List) — Aplicación Web en Python

Aplicación completa de gestión de tareas desarrollada exclusivamente con la **librería estándar de Python**, interfaz gráfica Web moderna en español (HTML5, CSS3 y JavaScript Vanilla) y persistencia automática en archivo JSON (`tareas.json`).

## Características Principales

- **Atributos completos por tarea**:
  - `titulo` (obligatorio)
  - `descripcion` (opcional)
  - `prioridad`: `baja`, `media`, `alta`
  - `estado`: `pendiente`, `en_progreso`, `completada`
  - `fecha_limite`: formato `YYYY-MM-DD`
  - `etiquetas`: lista de etiquetas personalizadas
  - `dependencias`: lista de IDs de tareas previas existentes
- **Gestión avanzada de dependencias**:
  - **Bloqueo de completado**: impide marcar una tarea como `completada` si alguna de sus tareas previas aún no está completada.
  - **Prevención de dependencias circulares**: detección de ciclos en el grafo de dependencias mediante búsqueda en profundidad (DFS).
- **Búsqueda y filtrado**:
  - Filtro por `estado`, `prioridad`, `etiqueta` y condición de vencimiento (`vencidas`).
  - Búsqueda de texto libre en título, descripción, etiquetas o ID.
- **Resumen estadístico en tiempo real**:
  - Total de tareas, pendientes, en progreso, completadas, **conteo de tareas vencidas**, tareas bloqueadas y porcentaje de avance global.

## Estructura del Proyecto

- `gestor_tareas.py`: Lógica de dominio, validaciones, detección de ciclos, bloqueo de completado y persistencia atómica en JSON.
- `app.py` / `main.py`: Servidor HTTP multihilo (`ThreadingHTTPServer`) y API RESTful en el puerto `8081` por defecto.
- `static/index.html`, `static/styles.css`, `static/app.js`: Interfaz gráfica Web moderna en español.
- `test_tareas.py`: Suite de pruebas unitarias y de integración con `unittest`.

## Cómo Ejecutar la Aplicación

1. Situarse en el directorio del proyecto:
   ```bash
   cd /tmp/benchmark_sesion_a_libre
   ```
2. Iniciar el servidor Web (usa el puerto `8081` por defecto):
   ```bash
   python3 app.py
   ```
3. Abrir en el navegador:
   ```
   http://localhost:8081
   ```

### Opciones adicionales de línea de comandos

```bash
python3 app.py --port 8081 --archivo tareas.json
```

## Cómo Ejecutar las Pruebas Automatizadas

```bash
cd /tmp/benchmark_sesion_a_libre
python3 -m unittest discover -v
```
