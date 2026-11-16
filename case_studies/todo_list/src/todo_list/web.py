"""Servidor HTTP WSGI y API REST JSON para la aplicación de Lista de Tareas."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
from http import HTTPStatus
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from todo_list.models import (
    CyclicDependencyError,
    DependencyNotCompletedError,
    InvalidDependencyError,
    TaskNotFoundError,
    TodoError,
    ValidationError,
)
from todo_list.repository import JsonTaskRepository
from todo_list.service import TaskFilter, TaskService

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8082
STATIC_DIR = Path(__file__).resolve().parent / "static"
DEFAULT_DATA_PATH = (
    Path(__file__).resolve().parent.parent.parent / "data" / "tasks.json"
)

StartResponse = Callable[[str, List[Tuple[str, str]]], Any]


class TodoWebApp:
    """Aplicación WSGI que sirve el panel Web estático y la API REST JSON."""

    def __init__(
        self,
        service: TaskService,
        static_dir: Optional[Path] = None,
    ) -> None:
        """Inicializa la aplicación WSGI con el servicio de negocio y carpeta estática.

        Args:
            service: Instancia de TaskService.
            static_dir: Directorio de archivos estáticos (HTML, CSS, JS).
        """
        self._service = service
        self._static_dir = (static_dir or STATIC_DIR).resolve()

    @property
    def service(self) -> TaskService:
        """Retorna el servicio de tareas asociado."""
        return self._service

    def __call__(
        self,
        environ: Dict[str, Any],
        start_response: StartResponse,
    ) -> Iterable[bytes]:
        """Punto de entrada estándar PEP 3333 (WSGI).

        Args:
            environ: Diccionario de entorno WSGI.
            start_response: Callback WSGI para iniciar respuesta HTTP.

        Returns:
            Iterable con el cuerpo de la respuesta en bytes.
        """
        method = str(environ.get("REQUEST_METHOD", "GET")).upper()
        path = str(environ.get("PATH_INFO", "/")) or "/"
        query_string = str(environ.get("QUERY_STRING", ""))

        try:
            if path.startswith("/api/"):
                status, payload = self._dispatch_api(method, path, query_string, environ)
                return self._json_response(start_response, status, payload)
            return self._serve_static(method, path, start_response)
        except TodoError as exc:
            err_status, err_payload = self._map_domain_error(exc)
            return self._json_response(start_response, err_status, err_payload)

    @staticmethod
    def _map_domain_error(exc: TodoError) -> Tuple[HTTPStatus, Dict[str, Any]]:
        """Traduce una excepción de dominio a su código HTTP y cuerpo JSON."""
        if isinstance(exc, TaskNotFoundError):
            return HTTPStatus.NOT_FOUND, {"error": str(exc), "error_type": "not_found"}
        if isinstance(exc, CyclicDependencyError):
            return (
                HTTPStatus.CONFLICT,
                {"error": str(exc), "error_type": "cyclic_dependency"},
            )
        if isinstance(exc, DependencyNotCompletedError):
            return (
                HTTPStatus.CONFLICT,
                {
                    "error": str(exc),
                    "error_type": "dependency_not_completed",
                    "blocking_ids": exc.blocking_ids,
                },
            )
        if isinstance(exc, InvalidDependencyError):
            return (
                HTTPStatus.BAD_REQUEST,
                {"error": str(exc), "error_type": "invalid_dependency"},
            )
        return (
            HTTPStatus.BAD_REQUEST,
            {"error": str(exc), "error_type": "validation_error"},
        )

    def _dispatch_api(  # pylint: disable=too-many-return-statements
        self,
        method: str,
        path: str,
        query_string: str,
        environ: Dict[str, Any],
    ) -> Tuple[HTTPStatus, Dict[str, Any]]:
        """Enruta las peticiones bajo el prefijo /api/."""
        normalized = path.rstrip("/")
        if normalized == "/api/health" and method == "GET":
            return HTTPStatus.OK, {"status": "ok"}

        if normalized == "/api/summary" and method == "GET":
            return HTTPStatus.OK, self._service.get_summary().to_dict()

        if normalized == "/api/tasks":
            if method == "GET":
                return HTTPStatus.OK, self._handle_list_tasks(query_string)
            if method == "POST":
                body = self._read_json_body(environ)
                return HTTPStatus.CREATED, self._handle_create_task(body)

        if normalized.startswith("/api/tasks/"):
            return self._dispatch_task_resource(method, normalized, environ)

        return (
            HTTPStatus.NOT_FOUND,
            {"error": f"Ruta o método no soportado: {method} {path}"},
        )

    def _dispatch_task_resource(
        self,
        method: str,
        normalized_path: str,
        environ: Dict[str, Any],
    ) -> Tuple[HTTPStatus, Dict[str, Any]]:
        """Enruta operaciones sobre una tarea específica (/api/tasks/<id>...)."""
        parts = [segment for segment in normalized_path.split("/") if segment]
        # parts esperados: ['api', 'tasks', '<task_id>', ...]
        if len(parts) == 3:
            task_id = parts[2]
            if method == "GET":
                task = self._service.get_task(task_id)
                return HTTPStatus.OK, {"task": self._service.enrich_task(task)}
            if method == "PUT":
                body = self._read_json_body(environ)
                return HTTPStatus.OK, self._handle_update_task(task_id, body)
            if method == "DELETE":
                self._service.delete_task(task_id)
                return HTTPStatus.OK, {
                    "deleted": task_id,
                    "summary": self._service.get_summary().to_dict(),
                }

        if len(parts) == 4:
            task_id, action = parts[2], parts[3]
            if action == "status" and method in ("PATCH", "PUT", "POST"):
                body = self._read_json_body(environ)
                new_status = body.get("status", "")
                updated = self._service.update_status(task_id, new_status)
                return HTTPStatus.OK, {
                    "task": self._service.enrich_task(updated),
                    "summary": self._service.get_summary().to_dict(),
                }
            if action == "complete" and method in ("POST", "PATCH"):
                completed = self._service.complete_task(task_id)
                return HTTPStatus.OK, {
                    "task": self._service.enrich_task(completed),
                    "summary": self._service.get_summary().to_dict(),
                }

        return (
            HTTPStatus.NOT_FOUND,
            {"error": f"Endpoint de tarea no válido: {method} {normalized_path}"},
        )

    def _handle_list_tasks(self, query_string: str) -> Dict[str, Any]:
        """Procesa GET /api/tasks con parámetros de filtro y búsqueda."""
        params = parse_qs(query_string, keep_blank_values=False)
        overdue_raw = (self._first_param(params, "overdue_only") or "").lower()
        criteria = TaskFilter(
            status=self._first_param(params, "status"),
            priority=self._first_param(params, "priority"),
            tag=self._first_param(params, "tag"),
            search=self._first_param(params, "search"),
            overdue_only=overdue_raw in ("1", "true", "yes", "si"),
        )
        all_tasks = self._service.repository.list_all()
        tasks_by_id = {item.id: item for item in all_tasks}
        filtered = self._service.list_tasks(filters=criteria)
        enriched = [
            self._service.enrich_task(task, tasks_by_id=tasks_by_id)
            for task in filtered
        ]
        return {
            "tasks": enriched,
            "summary": self._service.get_summary().to_dict(),
        }

    def _handle_create_task(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa POST /api/tasks."""
        created = self._service.create_task(
            title=body.get("title", ""),
            description=body.get("description", ""),
            priority=body.get("priority", "media"),
            status=body.get("status", "pendiente"),
            due_date=body.get("due_date"),
            tags=body.get("tags", []),
            dependencies=body.get("dependencies", []),
            task_id=body.get("id"),
        )
        return {
            "task": self._service.enrich_task(created),
            "summary": self._service.get_summary().to_dict(),
        }

    def _handle_update_task(
        self,
        task_id: str,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Procesa PUT /api/tasks/<id>."""
        allowed_fields = (
            "title",
            "description",
            "priority",
            "status",
            "due_date",
            "tags",
            "dependencies",
        )
        changes = {key: body[key] for key in allowed_fields if key in body}
        updated = self._service.update_task(task_id, **changes)
        return {
            "task": self._service.enrich_task(updated),
            "summary": self._service.get_summary().to_dict(),
        }

    def _serve_static(
        self,
        method: str,
        path: str,
        start_response: StartResponse,
    ) -> Iterable[bytes]:
        """Sirve archivos estáticos (HTML, CSS, JS) del directorio static/."""
        if method not in ("GET", "HEAD"):
            return self._json_response(
                start_response,
                HTTPStatus.METHOD_NOT_ALLOWED,
                {"error": "Método no permitido para recursos estáticos."},
            )

        relative_map = {
            "/": "index.html",
            "/index.html": "index.html",
            "/styles.css": "styles.css",
            "/app.js": "app.js",
            "/static/index.html": "index.html",
            "/static/styles.css": "styles.css",
            "/static/app.js": "app.js",
        }
        target_name = relative_map.get(path)
        if target_name is None:
            return self._json_response(
                start_response,
                HTTPStatus.NOT_FOUND,
                {"error": f"Recurso no encontrado: {path}"},
            )

        file_path = (self._static_dir / target_name).resolve()
        if not file_path.is_file():
            return self._json_response(
                start_response,
                HTTPStatus.NOT_FOUND,
                {"error": f"Archivo estático faltante: {target_name}"},
            )

        content_type, _ = mimetypes.guess_type(str(file_path))
        mime = content_type or "application/octet-stream"
        if mime.startswith("text/") or mime == "application/javascript":
            mime = f"{mime}; charset=utf-8"

        body = file_path.read_bytes()
        headers = [
            ("Content-Type", mime),
            ("Content-Length", str(len(body))),
            ("Cache-Control", "no-store"),
        ]
        status_line = f"{HTTPStatus.OK.value} {HTTPStatus.OK.phrase}"
        start_response(status_line, headers)
        return [b"" if method == "HEAD" else body]

    @staticmethod
    def _read_json_body(environ: Dict[str, Any]) -> Dict[str, Any]:
        """Lee y decodifica el cuerpo JSON de una petición WSGI."""
        try:
            content_length = int(environ.get("CONTENT_LENGTH") or 0)
        except ValueError as exc:
            raise ValidationError("Cabecera Content-Length inválida.") from exc

        if content_length <= 0:
            return {}

        stream = environ.get("wsgi.input")
        if stream is None:
            return {}

        raw_bytes = stream.read(content_length)
        if not raw_bytes:
            return {}

        try:
            decoded = json.loads(raw_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValidationError("El cuerpo de la petición no es JSON válido.") from exc

        if not isinstance(decoded, dict):
            raise ValidationError("El cuerpo JSON debe ser un objeto clave-valor.")
        return decoded

    @staticmethod
    def _first_param(
        params: Dict[str, List[str]],
        key: str,
    ) -> Optional[str]:
        """Extrae el primer valor no vacío de un parámetro de query string."""
        values = params.get(key)
        if not values:
            return None
        cleaned = values[0].strip()
        return cleaned if cleaned else None

    @staticmethod
    def _json_response(
        start_response: StartResponse,
        status: HTTPStatus,
        payload: Dict[str, Any],
    ) -> Iterable[bytes]:
        """Construye una respuesta HTTP con cuerpo JSON en UTF-8."""
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(encoded))),
            ("Cache-Control", "no-store"),
        ]
        status_line = f"{status.value} {status.phrase}"
        start_response(status_line, headers)
        return [encoded]


def create_app(
    data_path: Optional[Union[str, Path]] = None,
    static_dir: Optional[Path] = None,
) -> TodoWebApp:
    """Factoría para construir la aplicación WSGI con persistencia JSON.

    Args:
        data_path: Ruta opcional al archivo JSON de tareas.
        static_dir: Directorio opcional de archivos estáticos.

    Returns:
        Instancia configurada de TodoWebApp.
    """
    resolved_data = Path(
        data_path or os.environ.get("TODO_DATA_PATH", str(DEFAULT_DATA_PATH))
    )
    repository = JsonTaskRepository(resolved_data)
    service = TaskService(repository)
    return TodoWebApp(service=service, static_dir=static_dir)


def run_server(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    data_path: Optional[Union[str, Path]] = None,
) -> None:  # pragma: no cover
    """Inicia el servidor HTTP WSGI en el host y puerto indicados.

    Args:
        host: Dirección IP o hostname de escucha (por defecto 127.0.0.1).
        port: Puerto TCP de escucha (por defecto 8082).
        data_path: Ruta al archivo JSON de persistencia.
    """
    app = create_app(data_path=data_path)
    with make_server(host, port, app) as server:
        print(f"Servidor To-Do List activo en http://{host}:{port}")
        server.serve_forever()


def main(argv: Optional[List[str]] = None) -> int:
    """Punto de entrada CLI para iniciar el servidor o verificar configuración.

    Args:
        argv: Lista opcional de argumentos de línea de comandos.

    Returns:
        Código de salida (0 para éxito).
    """
    parser = argparse.ArgumentParser(
        description="Servidor Web para la aplicación de Lista de Tareas."
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("TODO_HOST", DEFAULT_HOST),
        help="Host de escucha HTTP (por defecto: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("TODO_PORT", str(DEFAULT_PORT))),
        help="Puerto HTTP (por defecto: 8082)",
    )
    parser.add_argument(
        "--data",
        default=os.environ.get("TODO_DATA_PATH", str(DEFAULT_DATA_PATH)),
        help="Ruta del archivo JSON de persistencia",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Valida la inicialización de la app y termina inmediatamente.",
    )
    args = parser.parse_args(argv)
    if args.check:
        create_app(data_path=args.data)
        return 0
    run_server(host=args.host, port=args.port, data_path=args.data)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
