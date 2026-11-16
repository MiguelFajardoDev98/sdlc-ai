#!/usr/bin/env python3
"""
Servidor Web y API REST para la aplicación de Lista de Tareas (To-Do List).
Implementado exclusivamente con la librería estándar de Python (http.server, json, urllib, etc.).
Puerto por defecto: 8081.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from urllib.parse import parse_qs, unquote, urlparse

from gestor_tareas import (
    ErrorDependenciaCircular,
    ErrorTareaBloqueada,
    ErrorTareaNoEncontrada,
    ErrorValidacionTarea,
    GestorTareas,
)

DIRECTORIO_BASE = Path(__file__).resolve().parent
DIRECTORIO_ESTATICO = DIRECTORIO_BASE / "static"
RUTA_JSON_DEFECTO = DIRECTORIO_BASE / "tareas.json"
PUERTO_DEFECTO = 8081


class ManejadorTareasHTTP(BaseHTTPRequestHandler):
    """Manejador HTTP para servir la interfaz Web moderna y la API REST de tareas."""

    gestor: GestorTareas = None  # type: ignore

    def log_message(self, format: str, *args: Any) -> None:
        """Registro silencioso o formateado en consola."""
        if os.environ.get("SILENCIAR_LOGS_HTTP") == "1":
            return
        sys.stderr.write(
            f"[{self.log_date_time_string()}] {self.address_string()} - {format % args}\n"
        )

    def _enviar_json(self, codigo: int, payload: Dict[str, Any]) -> None:
        cuerpo = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(cuerpo)

    def _enviar_archivo_estatico(self, ruta_archivo: Path) -> None:
        if not ruta_archivo.exists() or not ruta_archivo.is_file():
            self._enviar_json(
                HTTPStatus.NOT_FOUND,
                {"ok": False, "error": "Recurso estático no encontrado."},
            )
            return

        tipo_mime, _ = mimetypes.guess_type(str(ruta_archivo))
        if not tipo_mime:
            tipo_mime = "application/octet-stream"
        if tipo_mime.startswith("text/") or tipo_mime in ("application/javascript", "application/json"):
            tipo_mime = f"{tipo_mime}; charset=utf-8"

        contenido = ruta_archivo.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", tipo_mime)
        self.send_header("Content-Length", str(len(contenido)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(contenido)

    def _leer_cuerpo_json(self) -> Dict[str, Any]:
        longitud_str = self.headers.get("Content-Length", "0")
        try:
            longitud = int(longitud_str)
        except ValueError:
            longitud = 0

        if longitud <= 0:
            return {}

        crudo = self.rfile.read(longitud).decode("utf-8")
        if not crudo.strip():
            return {}
        try:
            datos = json.loads(crudo)
            if not isinstance(datos, dict):
                raise ErrorValidacionTarea("El cuerpo de la petición JSON debe ser un objeto.")
            return datos
        except json.JSONDecodeError as exc:
            raise ErrorValidacionTarea(f"JSON mal formado en la solicitud: {exc.msg}") from exc

    def _manejar_excepcion_negocio(self, exc: Exception) -> None:
        if isinstance(exc, ErrorTareaNoEncontrada):
            self._enviar_json(
                HTTPStatus.NOT_FOUND,
                {"ok": False, "codigo": "NO_ENCONTRADA", "error": str(exc.args[0] if exc.args else exc)},
            )
        elif isinstance(exc, ErrorDependenciaCircular):
            self._enviar_json(
                HTTPStatus.BAD_REQUEST,
                {"ok": False, "codigo": "DEPENDENCIA_CIRCULAR", "error": str(exc)},
            )
        elif isinstance(exc, ErrorTareaBloqueada):
            self._enviar_json(
                HTTPStatus.BAD_REQUEST,
                {"ok": False, "codigo": "TAREA_BLOQUEADA", "error": str(exc)},
            )
        elif isinstance(exc, ErrorValidacionTarea):
            self._enviar_json(
                HTTPStatus.BAD_REQUEST,
                {"ok": False, "codigo": "ERROR_VALIDACION", "error": str(exc)},
            )
        else:
            self._enviar_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"ok": False, "codigo": "ERROR_INTERNO", "error": f"Error interno del servidor: {exc}"},
            )

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        url = urlparse(self.path)
        ruta = unquote(url.path)
        parametros = parse_qs(url.query)

        try:
            if ruta in ("/", "/index.html"):
                self._enviar_archivo_estatico(DIRECTORIO_ESTATICO / "index.html")
                return

            if ruta.startswith("/static/"):
                relativo = ruta[len("/static/"):]
                ruta_segura = (DIRECTORIO_ESTATICO / relativo).resolve()
                if not str(ruta_segura).startswith(str(DIRECTORIO_ESTATICO.resolve())):
                    self._enviar_json(HTTPStatus.FORBIDDEN, {"ok": False, "error": "Acceso denegado."})
                    return
                self._enviar_archivo_estatico(ruta_segura)
                return

            if ruta in ("/styles.css", "/app.js"):
                self._enviar_archivo_estatico(DIRECTORIO_ESTATICO / ruta.lstrip("/"))
                return

            if ruta in ("/api/estadisticas", "/api/estadisticas/"):
                estadisticas = self.gestor.obtener_estadisticas()
                respuesta = {"ok": True, "estadisticas": estadisticas}
                respuesta.update(estadisticas)
                self._enviar_json(HTTPStatus.OK, respuesta)
                return

            if ruta in ("/api/tareas", "/api/tareas/"):
                estado = parametros.get("estado", [None])[0]
                prioridad = parametros.get("prioridad", [None])[0]
                busqueda = (
                    parametros.get("busqueda", [None])[0]
                    or parametros.get("q", [None])[0]
                    or parametros.get("buscar", [None])[0]
                )
                etiqueta = parametros.get("etiqueta", [None])[0]
                vencidas_str = parametros.get("vencidas", [None])[0]
                vencidas: Optional[bool] = None
                if vencidas_str is not None and vencidas_str.strip() != "":
                    if vencidas_str.strip().lower() in ("true", "1", "si", "sí"):
                        vencidas = True
                    elif vencidas_str.strip().lower() in ("false", "0", "no"):
                        vencidas = False

                tareas = self.gestor.listar_tareas(
                    estado=estado,
                    prioridad=prioridad,
                    busqueda=busqueda,
                    etiqueta=etiqueta,
                    vencidas=vencidas,
                )
                estadisticas = self.gestor.obtener_estadisticas()
                self._enviar_json(
                    HTTPStatus.OK,
                    {
                        "ok": True,
                        "total_filtradas": len(tareas),
                        "tareas": tareas,
                        "estadisticas": estadisticas,
                    },
                )
                return

            coincidencia_tarea = re.match(r"^/api/tareas/([^/]+)/?$", ruta)
            if coincidencia_tarea:
                tarea_id = coincidencia_tarea.group(1)
                tarea = self.gestor.obtener_tarea(tarea_id)
                self._enviar_json(HTTPStatus.OK, {"ok": True, "tarea": tarea})
                return

            self._enviar_json(
                HTTPStatus.NOT_FOUND,
                {"ok": False, "error": f"Ruta '{ruta}' no encontrada."},
            )
        except Exception as exc:
            self._manejar_excepcion_negocio(exc)

    def do_POST(self) -> None:
        url = urlparse(self.path)
        ruta = unquote(url.path)

        try:
            if ruta in ("/api/tareas", "/api/tareas/"):
                datos = self._leer_cuerpo_json()
                nueva = self.gestor.crear_tarea(
                    titulo=datos.get("titulo", ""),
                    descripcion=datos.get("descripcion", ""),
                    prioridad=datos.get("prioridad", "media"),
                    estado=datos.get("estado", "pendiente"),
                    fecha_limite=datos.get("fecha_limite"),
                    etiquetas=datos.get("etiquetas", []),
                    dependencias=datos.get("dependencias", []),
                    tarea_id=datos.get("id"),
                )
                estadisticas = self.gestor.obtener_estadisticas()
                self._enviar_json(
                    HTTPStatus.CREATED,
                    {
                        "ok": True,
                        "mensaje": "Tarea creada correctamente.",
                        "tarea": nueva,
                        "estadisticas": estadisticas,
                    },
                )
                return

            coincidencia_completar = re.match(r"^/api/tareas/([^/]+)/completar/?$", ruta)
            if coincidencia_completar:
                tarea_id = coincidencia_completar.group(1)
                actualizada = self.gestor.completar_tarea(tarea_id)
                estadisticas = self.gestor.obtener_estadisticas()
                self._enviar_json(
                    HTTPStatus.OK,
                    {
                        "ok": True,
                        "mensaje": "Tarea marcada como completada.",
                        "tarea": actualizada,
                        "estadisticas": estadisticas,
                    },
                )
                return

            coincidencia_estado = re.match(r"^/api/tareas/([^/]+)/estado/?$", ruta)
            if coincidencia_estado:
                tarea_id = coincidencia_estado.group(1)
                datos = self._leer_cuerpo_json()
                nuevo_estado = datos.get("estado", "")
                actualizada = self.gestor.cambiar_estado(tarea_id, nuevo_estado)
                estadisticas = self.gestor.obtener_estadisticas()
                self._enviar_json(
                    HTTPStatus.OK,
                    {
                        "ok": True,
                        "mensaje": f"Estado actualizado a '{nuevo_estado}'.",
                        "tarea": actualizada,
                        "estadisticas": estadisticas,
                    },
                )
                return

            self._enviar_json(
                HTTPStatus.NOT_FOUND,
                {"ok": False, "error": f"Ruta POST '{ruta}' no encontrada."},
            )
        except Exception as exc:
            self._manejar_excepcion_negocio(exc)

    def do_PUT(self) -> None:
        self._manejar_actualizacion_http()

    def do_PATCH(self) -> None:
        self._manejar_actualizacion_http()

    def _manejar_actualizacion_http(self) -> None:
        url = urlparse(self.path)
        ruta = unquote(url.path)

        try:
            coincidencia_completar = re.match(r"^/api/tareas/([^/]+)/completar/?$", ruta)
            if coincidencia_completar:
                tarea_id = coincidencia_completar.group(1)
                actualizada = self.gestor.completar_tarea(tarea_id)
                estadisticas = self.gestor.obtener_estadisticas()
                self._enviar_json(
                    HTTPStatus.OK,
                    {
                        "ok": True,
                        "mensaje": "Tarea marcada como completada.",
                        "tarea": actualizada,
                        "estadisticas": estadisticas,
                    },
                )
                return

            coincidencia_tarea = re.match(r"^/api/tareas/([^/]+)/?$", ruta)
            if coincidencia_tarea:
                tarea_id = coincidencia_tarea.group(1)
                cambios = self._leer_cuerpo_json()
                actualizada = self.gestor.actualizar_tarea(tarea_id, cambios)
                estadisticas = self.gestor.obtener_estadisticas()
                self._enviar_json(
                    HTTPStatus.OK,
                    {
                        "ok": True,
                        "mensaje": "Tarea actualizada correctamente.",
                        "tarea": actualizada,
                        "estadisticas": estadisticas,
                    },
                )
                return

            self._enviar_json(
                HTTPStatus.NOT_FOUND,
                {"ok": False, "error": f"Ruta de actualización '{ruta}' no encontrada."},
            )
        except Exception as exc:
            self._manejar_excepcion_negocio(exc)

    def do_DELETE(self) -> None:
        url = urlparse(self.path)
        ruta = unquote(url.path)

        try:
            coincidencia_tarea = re.match(r"^/api/tareas/([^/]+)/?$", ruta)
            if coincidencia_tarea:
                tarea_id = coincidencia_tarea.group(1)
                eliminada = self.gestor.eliminar_tarea(tarea_id)
                estadisticas = self.gestor.obtener_estadisticas()
                self._enviar_json(
                    HTTPStatus.OK,
                    {
                        "ok": True,
                        "mensaje": "Tarea eliminada correctamente.",
                        "tarea": eliminada,
                        "estadisticas": estadisticas,
                    },
                )
                return

            self._enviar_json(
                HTTPStatus.NOT_FOUND,
                {"ok": False, "error": f"Ruta DELETE '{ruta}' no encontrada."},
            )
        except Exception as exc:
            self._manejar_excepcion_negocio(exc)


def crear_servidor(
    host: str = "127.0.0.1",
    puerto: int = PUERTO_DEFECTO,
    ruta_archivo: str | Path = RUTA_JSON_DEFECTO,
) -> Tuple[ThreadingHTTPServer, GestorTareas]:
    """Crea y configura una instancia del servidor HTTP junto con su GestorTareas."""
    gestor = GestorTareas(ruta_archivo=ruta_archivo)

    class ManejadorConfigurado(ManejadorTareasHTTP):
        pass

    ManejadorConfigurado.gestor = gestor
    servidor = ThreadingHTTPServer((host, puerto), ManejadorConfigurado)
    return servidor, gestor


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Servidor Web de Lista de Tareas (To-Do List) en Python estándar."
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("HOST", "0.0.0.0"),
        help="Dirección IP o host donde escuchar (por defecto: 0.0.0.0 / localhost).",
    )
    parser.add_argument(
        "--port",
        "--puerto",
        dest="puerto",
        type=int,
        default=int(os.environ.get("PORT", PUERTO_DEFECTO)),
        help=f"Puerto HTTP del servidor (por defecto: {PUERTO_DEFECTO}).",
    )
    parser.add_argument(
        "--archivo",
        default=os.environ.get("TAREAS_JSON", str(RUTA_JSON_DEFECTO)),
        help="Ruta del archivo JSON de persistencia (por defecto: tareas.json).",
    )
    args = parser.parse_args()

    servidor, _ = crear_servidor(
        host=args.host,
        puerto=args.puerto,
        ruta_archivo=args.archivo,
    )
    host_mostrar = "localhost" if args.host in ("0.0.0.0", "127.0.0.1") else args.host
    print(f"Servidor de Lista de Tareas iniciado en http://{host_mostrar}:{args.puerto}")
    print(f"Archivo de persistencia JSON: {Path(args.archivo).resolve()}")
    print("Presiona Ctrl+C para detener el servidor.")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nDeteniendo el servidor...")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
