"""Suite integral de pruebas unitarias y de integración para todo_list."""

from __future__ import annotations

import io
import json
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pytest

from todo_list.models import (
    CyclicDependencyError,
    DependencyNotCompletedError,
    InvalidDependencyError,
    Priority,
    Task,
    TaskNotFoundError,
    TaskStatus,
    ValidationError,
    normalize_dependencies,
    normalize_tags,
    validate_due_date,
)
from todo_list.repository import JsonTaskRepository
from todo_list.service import TaskService
from todo_list.web import TodoWebApp, create_app, main


def call_wsgi(
    app: TodoWebApp,
    method: str,
    path: str,
    **options: Any,
) -> Tuple[int, Dict[str, str], bytes]:
    """Ejecuta una petición sintética WSGI contra TodoWebApp."""
    query_string = str(options.get("query_string", ""))
    body = options.get("body")
    raw_body = options.get("raw_body")
    if raw_body is not None:
        payload_bytes = raw_body
    elif body is not None:
        payload_bytes = json.dumps(body).encode("utf-8")
    else:
        payload_bytes = b""

    environ: Dict[str, Any] = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "QUERY_STRING": query_string,
        "CONTENT_LENGTH": str(len(payload_bytes)),
        "CONTENT_TYPE": "application/json",
        "wsgi.input": io.BytesIO(payload_bytes),
    }

    captured: Dict[str, Any] = {}

    def start_response(
        status: str,
        headers: List[Tuple[str, str]],
    ) -> None:
        captured["status"] = int(status.split(" ", 1)[0])
        captured["headers"] = dict(headers)

    response_chunks = list(app(environ, start_response))
    response_bytes = b"".join(response_chunks)
    return captured["status"], captured["headers"], response_bytes


# =====================================================================
# 1. PRUEBAS DE MODELOS Y VALIDACIONES DE DOMINIO
# =====================================================================


def test_task_creation_and_normalization() -> None:
    """Verifica creación válida, normalización de etiquetas y serialización."""
    task = Task(
        title="  Implementar API REST  ",
        description="  Servidor WSGI estándar  ",
        priority="ALTA",  # type: ignore[arg-type]
        status="en_progreso",  # type: ignore[arg-type]
        due_date="2026-12-15",
        tags=["Backend", " backend ", "URGENTE", ""],
        dependencies=["dep-1", "dep-1", " dep-2 "],
    )
    assert task.title == "Implementar API REST"
    assert task.description == "Servidor WSGI estándar"
    assert task.priority == Priority.ALTA
    assert task.status == TaskStatus.EN_PROGRESO
    assert task.due_date == "2026-12-15"
    assert task.tags == ["backend", "urgente"]
    assert task.dependencies == ["dep-1", "dep-2"]

    serialized = task.to_dict()
    rebuilt = Task.from_dict(serialized)
    assert rebuilt.id == task.id
    assert rebuilt.title == task.title
    assert rebuilt.tags == ["backend", "urgente"]


def test_task_validation_errors() -> None:
    """Verifica que entradas inválidas lancen ValidationError o subclases."""
    with pytest.raises(ValidationError):
        Task(title="   ")

    with pytest.raises(ValidationError):
        Task(title="x" * 201)

    with pytest.raises(ValidationError):
        Task(title="Tarea", id="   ")

    with pytest.raises(ValidationError):
        Task(title=123)  # type: ignore[arg-type]

    with pytest.raises(ValidationError):
        Task(title="Tarea", description=123)  # type: ignore[arg-type]

    with pytest.raises(ValidationError):
        Priority.from_value("urgente")

    with pytest.raises(ValidationError):
        Priority.from_value(10)  # type: ignore[arg-type]

    with pytest.raises(ValidationError):
        TaskStatus.from_value("cancelada")

    with pytest.raises(ValidationError):
        TaskStatus.from_value(None)  # type: ignore[arg-type]

    with pytest.raises(InvalidDependencyError):
        Task(id="t-1", title="Auto ref", dependencies=["t-1"])


def test_date_tags_and_dependencies_validators() -> None:
    """Verifica validaciones de fechas límite, etiquetas y dependencias."""
    assert validate_due_date(None) is None
    assert validate_due_date("   ") is None
    assert validate_due_date("2026-02-28") == "2026-02-28"

    with pytest.raises(ValidationError):
        validate_due_date("28-02-2026")

    with pytest.raises(ValidationError):
        validate_due_date("2026-02-30")

    with pytest.raises(ValidationError):
        validate_due_date(20260228)  # type: ignore[arg-type]

    with pytest.raises(ValidationError):
        normalize_tags("no-es-lista")

    with pytest.raises(ValidationError):
        normalize_tags([123])  # type: ignore[list-item]

    with pytest.raises(ValidationError):
        normalize_dependencies("no-es-lista")

    with pytest.raises(ValidationError):
        normalize_dependencies([123])  # type: ignore[list-item]

    with pytest.raises(ValidationError):
        normalize_dependencies(["   "])

    with pytest.raises(ValidationError):
        Task.from_dict(["no-es-dict"])  # type: ignore[arg-type]


def test_task_overdue_calculation() -> None:
    """Verifica que solo las tareas no completadas con fecha pasada estén vencidas."""
    ref = date(2026, 6, 15)
    overdue_task = Task(
        title="Vencida",
        due_date="2026-06-10",
        status=TaskStatus.PENDIENTE,
    )
    completed_past_task = Task(
        title="Completada antes",
        due_date="2026-06-10",
        status=TaskStatus.COMPLETADA,
    )
    future_task = Task(
        title="Futura",
        due_date="2026-06-20",
        status=TaskStatus.EN_PROGRESO,
    )
    no_date_task = Task(title="Sin fecha")

    assert overdue_task.is_overdue(ref) is True
    assert completed_past_task.is_overdue(ref) is False
    assert future_task.is_overdue(ref) is False
    assert no_date_task.is_overdue(ref) is False


# =====================================================================
# 2. PRUEBAS DE REPOSITORIO Y PERSISTENCIA JSON
# =====================================================================


def test_repository_crud_and_corrupted_recovery(tmp_path: Path) -> None:
    """Verifica persistencia JSON, archivos vacíos y recuperación ante corrupción."""
    json_file = tmp_path / "subdir" / "tasks.json"
    repo = JsonTaskRepository(json_file)
    assert repo.file_path == json_file
    assert repo.list_all() == []

    # Archivo vacío (0 bytes)
    json_file.write_text("", encoding="utf-8")
    assert repo.list_all() == []

    # Archivo corrupto
    json_file.write_text("{corrupt json...", encoding="utf-8")
    assert repo.list_all() == []
    assert repo.corrupted_recoveries == 1
    assert json_file.with_suffix(".json.corrupt").exists()

    # Estructura raíz inválida (ej. entero)
    json_file.write_text("42", encoding="utf-8")
    assert repo.list_all() == []
    assert repo.corrupted_recoveries == 2

    # Formato alternativo {"tasks": [...]}
    sample = Task(id="t-100", title="Desde objeto raíz").to_dict()
    json_file.write_text(json.dumps({"tasks": [sample]}), encoding="utf-8")
    loaded = repo.list_all()
    assert len(loaded) == 1
    assert loaded[0].id == "t-100"

    # Upsert y Delete
    updated = Task(id="t-100", title="Título actualizado")
    repo.upsert(updated)
    assert repo.get_by_id("t-100") is not None
    assert repo.get_by_id("t-100").title == "Título actualizado"  # type: ignore[union-attr]

    repo.upsert(Task(id="t-200", title="Segunda"))
    assert len(repo.list_all()) == 2
    assert repo.delete("t-100") is True
    assert repo.delete("no-existe") is False
    assert repo.get_by_id("t-100") is None


# =====================================================================
# 3. PRUEBAS DE SERVICIO DE NEGOCIO (DEPENDENCIAS, CICLOS, FILTROS, KPIS)
# =====================================================================


def test_service_cycle_detection_and_invalid_dependencies(tmp_path: Path) -> None:
    """Verifica detección de ciclos directos e indirectos y dependencias inválidas."""
    service = TaskService(JsonTaskRepository(tmp_path / "tasks.json"))
    t1 = service.create_task(title="Tarea 1", task_id="t1")
    t2 = service.create_task(title="Tarea 2", task_id="t2", dependencies=[t1.id])
    t3 = service.create_task(title="Tarea 3", task_id="t3", dependencies=[t2.id])

    # ID duplicado
    with pytest.raises(InvalidDependencyError):
        service.create_task(title="Duplicada", task_id="t1")

    # Dependencia inexistente
    with pytest.raises(InvalidDependencyError):
        service.create_task(title="Inválida", dependencies=["id-fantasma"])

    # Ciclo directo: t1 -> t2 -> t1
    with pytest.raises(CyclicDependencyError):
        service.update_task(t1.id, dependencies=[t2.id])

    # Ciclo indirecto de 3 nodos: t1 -> t3 -> t2 -> t1
    with pytest.raises(CyclicDependencyError):
        service.update_task(t1.id, dependencies=[t3.id])


def test_service_completion_blocking_and_reopen_guard(tmp_path: Path) -> None:
    """Verifica bloqueo al completar con previas pendientes y protección al reabrir."""
    service = TaskService(JsonTaskRepository(tmp_path / "tasks.json"))
    base = service.create_task(title="Base", task_id="base")
    dependent = service.create_task(
        title="Dependiente",
        task_id="dep",
        dependencies=[base.id],
    )

    # Intentar crear tarea ya completada con dependencia pendiente
    with pytest.raises(DependencyNotCompletedError):
        service.create_task(
            title="Inválida al nacer",
            status="completada",
            dependencies=[base.id],
        )

    # Intentar completar `dependent` mientras `base` está pendiente
    with pytest.raises(DependencyNotCompletedError) as exc_info:
        service.complete_task(dependent.id)
    assert base.id in exc_info.value.blocking_ids

    # Completar `base` y luego `dependent`
    service.complete_task(base.id)
    completed_dep = service.complete_task(dependent.id)
    assert completed_dep.status == TaskStatus.COMPLETADA

    # Intentar reabrir `base` mientras `dependent` sigue completada
    with pytest.raises(DependencyNotCompletedError):
        service.update_status(base.id, TaskStatus.PENDIENTE)


def test_service_delete_cleans_dependencies_and_filters_summary(tmp_path: Path) -> None:
    """Verifica limpieza de dependencias al borrar, filtros combinados y resumen."""
    service = TaskService(JsonTaskRepository(tmp_path / "tasks.json"))
    ref_date = date(2026, 5, 10)

    t1 = service.create_task(
        title="Configurar servidor Linux",
        description="Instalar paquetes base",
        priority="alta",
        status="pendiente",
        due_date="2026-05-01",
        tags=["infra", "linux"],
        task_id="t1",
    )
    t2 = service.create_task(
        title="Desplegar aplicación Python",
        description="Usar wsgiref en puerto 8082",
        priority="media",
        status="en_progreso",
        due_date="2026-05-20",
        tags=["python", "web"],
        dependencies=[t1.id],
        task_id="t2",
    )
    t3 = service.create_task(
        title="Documentar arquitectura",
        description="Diagramas Mermaid",
        priority="baja",
        status="completada",
        due_date="2026-05-01",
        tags=["docs"],
        task_id="t3",
    )

    summary = service.get_summary(reference_date=ref_date)
    assert t3.id == "t3"
    assert summary.total == 3
    assert summary.by_status == {
        "pendiente": 1,
        "en_progreso": 1,
        "completada": 1,
    }
    assert summary.by_priority == {"alta": 1, "media": 1, "baja": 1}
    assert summary.overdue_count == 1  # Solo t1 (t3 está completada)
    assert summary.blocked_count == 1  # t2 depende de t1 no completada
    assert summary.completion_rate == 33.33

    # Filtros y búsqueda
    assert len(service.list_tasks(status="pendiente")) == 1
    assert len(service.list_tasks(priority="media")) == 1
    assert len(service.list_tasks(tag="LINUX")) == 1
    assert len(service.list_tasks(search="wsgiref")) == 1
    assert len(service.list_tasks(search="docs")) == 1
    assert len(service.list_tasks(overdue_only=True, reference_date=ref_date)) == 1

    # Eliminar t1 debe limpiar la dependencia en t2
    service.delete_task(t1.id)
    updated_t2 = service.get_task(t2.id)
    assert updated_t2.dependencies == []

    with pytest.raises(TaskNotFoundError):
        service.get_task("inexistente")

    with pytest.raises(TaskNotFoundError):
        service.update_task("inexistente", title="Nada")

    with pytest.raises(TaskNotFoundError):
        service.delete_task("inexistente")


# =====================================================================
# 4. PRUEBAS DE SERVIDOR WEB WSGI Y ENDPOINTS API REST
# =====================================================================


def test_web_static_assets(tmp_path: Path) -> None:
    """Verifica entrega de activos estáticos HTML, CSS y JS y CLI --check."""
    data_file = tmp_path / "static_tasks.json"
    app = create_app(data_path=data_file)
    assert app.service is not None
    assert main(["--check", "--data", str(data_file)]) == 0

    status, headers, html_body = call_wsgi(app, "GET", "/")
    assert status == 200
    assert "text/html" in headers["Content-Type"]
    assert "Gestor de Tareas" in html_body.decode("utf-8")

    status, _, _ = call_wsgi(app, "HEAD", "/static/styles.css")
    assert status == 200

    status, _, _ = call_wsgi(app, "GET", "/static/app.js")
    assert status == 200

    status, _, _ = call_wsgi(app, "POST", "/static/app.js")
    assert status == 405

    status, _, _ = call_wsgi(app, "GET", "/no-existe.txt")
    assert status == 404


def test_web_rest_api_lifecycle(tmp_path: Path) -> None:
    """Verifica el ciclo completo REST HTTP (CRUD, ciclos, bloqueos y resumen)."""
    data_file = tmp_path / "api_tasks.json"
    app = create_app(data_path=data_file)

    # Health & Summary inicial
    status, _, body = call_wsgi(app, "GET", "/api/health")
    assert status == 200
    assert json.loads(body)["status"] == "ok"

    # Crear dos tareas vía POST /api/tasks
    status, _, body = call_wsgi(
        app,
        "POST",
        "/api/tasks",
        body={
            "id": "api-1",
            "title": "Diseñar modelo",
            "priority": "alta",
            "due_date": "2020-01-01",
            "tags": ["arquitectura"],
        },
    )
    assert status == 201
    created_1 = json.loads(body)["task"]
    assert created_1["id"] == "api-1"
    assert created_1["is_overdue"] is True

    status, _, body = call_wsgi(
        app,
        "POST",
        "/api/tasks",
        body={
            "id": "api-2",
            "title": "Codificar servicio",
            "priority": "media",
            "dependencies": ["api-1"],
        },
    )
    assert status == 201
    created_2 = json.loads(body)["task"]
    assert created_2["is_blocked"] is True

    # Intentar completar api-2 estando api-1 pendiente -> 409 Conflict
    status, _, body = call_wsgi(app, "POST", "/api/tasks/api-2/complete")
    assert status == 409
    err_payload = json.loads(body)
    assert err_payload["error_type"] == "dependency_not_completed"
    assert "api-1" in err_payload["blocking_ids"]

    # Intentar crear ciclo api-1 -> api-2 -> 409 Conflict
    status, _, body = call_wsgi(
        app,
        "PUT",
        "/api/tasks/api-1",
        body={"dependencies": ["api-2"]},
    )
    assert status == 409
    assert json.loads(body)["error_type"] == "cyclic_dependency"

    # Filtrar listado GET /api/tasks
    status, _, body = call_wsgi(
        app,
        "GET",
        "/api/tasks",
        query_string="priority=alta&overdue_only=true&search=modelo",
    )
    assert status == 200
    listed = json.loads(body)["tasks"]
    assert len(listed) == 1
    assert listed[0]["id"] == "api-1"

    # Consultar detalle individual GET /api/tasks/api-1
    status, _, body = call_wsgi(app, "GET", "/api/tasks/api-1")
    assert status == 200
    assert json.loads(body)["task"]["title"] == "Diseñar modelo"

    # Cambiar estado de api-1 a completada y luego completar api-2
    status, _, _ = call_wsgi(
        app,
        "PATCH",
        "/api/tasks/api-1/status",
        body={"status": "completada"},
    )
    assert status == 200

    status, _, _ = call_wsgi(app, "POST", "/api/tasks/api-2/complete")
    assert status == 200

    # Summary tras completar ambas
    status, _, body = call_wsgi(app, "GET", "/api/summary")
    assert status == 200
    summary_data = json.loads(body)
    assert summary_data["completion_rate"] == 100.0
    assert summary_data["overdue_count"] == 0

    # Eliminar tarea DELETE /api/tasks/api-2
    status, _, _ = call_wsgi(app, "DELETE", "/api/tasks/api-2")
    assert status == 200


def test_web_api_error_handling(tmp_path: Path) -> None:
    """Verifica respuestas HTTP 400 y 404 ante entradas y rutas inválidas."""
    data_file = tmp_path / "api_errors.json"
    app = create_app(data_path=data_file)
    call_wsgi(app, "POST", "/api/tasks", body={"id": "api-1", "title": "Base"})

    status, _, _ = call_wsgi(app, "GET", "/api/tasks/no-existe")
    assert status == 404

    status, _, _ = call_wsgi(app, "GET", "/api/unknown")
    assert status == 404

    status, _, _ = call_wsgi(app, "POST", "/api/tasks/api-1/unknown")
    assert status == 404

    status, _, _ = call_wsgi(
        app,
        "POST",
        "/api/tasks",
        raw_body=b"{invalid-json",
    )
    assert status == 400

    status, _, _ = call_wsgi(
        app,
        "POST",
        "/api/tasks",
        raw_body=b"[1, 2, 3]",
    )
    assert status == 400

    status, _, _ = call_wsgi(
        app,
        "POST",
        "/api/tasks",
        body={"title": "Dep fantasma", "dependencies": ["fantasma"]},
    )
    assert status == 400
