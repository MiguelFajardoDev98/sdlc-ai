#!/usr/bin/env python3
"""
Pruebas unitarias y de integración para la aplicación de Lista de Tareas (To-Do List).
Ejecutable con la librería estándar: python3 -m unittest discover -v
"""

from __future__ import annotations

import json
import os
import tempfile
import threading
import unittest
from datetime import date, timedelta
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from app import crear_servidor
from gestor_tareas import (
    ErrorDependenciaCircular,
    ErrorTareaBloqueada,
    ErrorTareaNoEncontrada,
    ErrorValidacionTarea,
    GestorTareas,
)


class TestGestorTareasDominio(unittest.TestCase):
    """Pruebas de la lógica de negocio y persistencia en JSON."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.ruta_json = Path(self.temp_dir.name) / "tareas_test.json"
        self.gestor = GestorTareas(ruta_archivo=self.ruta_json)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_crear_y_persistir_tarea_en_json(self) -> None:
        tarea = self.gestor.crear_tarea(
            titulo="Configurar servidor",
            descripcion="Servidor HTTP con librería estándar",
            prioridad="alta",
            estado="pendiente",
            fecha_limite="2026-12-31",
            etiquetas=["backend", "python"],
        )
        self.assertEqual(tarea["titulo"], "Configurar servidor")
        self.assertEqual(tarea["prioridad"], "alta")
        self.assertEqual(tarea["estado"], "pendiente")
        self.assertEqual(tarea["fecha_limite"], "2026-12-31")
        self.assertEqual(tarea["etiquetas"], ["backend", "python"])
        self.assertTrue(self.ruta_json.exists())

        # Recargar desde un nuevo gestor para comprobar persistencia JSON real
        otro_gestor = GestorTareas(ruta_archivo=self.ruta_json)
        recuperada = otro_gestor.obtener_tarea(tarea["id"])
        self.assertEqual(recuperada["titulo"], "Configurar servidor")
        self.assertEqual(recuperada["etiquetas"], ["backend", "python"])

    def test_validaciones_campos(self) -> None:
        with self.assertRaises(ErrorValidacionTarea):
            self.gestor.crear_tarea(titulo="")

        with self.assertRaises(ErrorValidacionTarea):
            self.gestor.crear_tarea(titulo="Prioridad inválida", prioridad="urgente")

        with self.assertRaises(ErrorValidacionTarea):
            self.gestor.crear_tarea(titulo="Estado inválido", estado="cancelada")

        with self.assertRaises(ErrorValidacionTarea):
            self.gestor.crear_tarea(titulo="Fecha inválida", fecha_limite="31-12-2026")

    def test_bloqueo_completar_con_dependencias_incompletas(self) -> None:
        t1 = self.gestor.crear_tarea(titulo="Diseñar esquema", prioridad="alta", estado="pendiente")
        t2 = self.gestor.crear_tarea(
            titulo="Implementar modelo",
            prioridad="media",
            estado="en_progreso",
            dependencias=[t1["id"]],
        )

        # Intentar completar t2 mientras t1 sigue pendiente debe fallar
        with self.assertRaises(ErrorTareaBloqueada):
            self.gestor.completar_tarea(t2["id"])

        # Completar t1 primero y luego t2 debe funcionar
        self.gestor.completar_tarea(t1["id"])
        t2_completada = self.gestor.completar_tarea(t2["id"])
        self.assertEqual(t2_completada["estado"], "completada")
        self.assertFalse(t2_completada["bloqueada"])

    def test_prevencion_dependencias_circulares(self) -> None:
        a = self.gestor.crear_tarea(titulo="Tarea A")
        b = self.gestor.crear_tarea(titulo="Tarea B", dependencias=[a["id"]])
        c = self.gestor.crear_tarea(titulo="Tarea C", dependencias=[b["id"]])

        # Dependencia directa consigo misma (A -> A)
        with self.assertRaises(ErrorDependenciaCircular):
            self.gestor.actualizar_tarea(a["id"], {"dependencias": [a["id"]]})

        # Ciclo de 2 nodos (A -> B -> A)
        with self.assertRaises(ErrorDependenciaCircular):
            self.gestor.actualizar_tarea(a["id"], {"dependencias": [b["id"]]})

        # Ciclo transitivo de 3 nodos (A -> C -> B -> A)
        with self.assertRaises(ErrorDependenciaCircular):
            self.gestor.actualizar_tarea(a["id"], {"dependencias": [c["id"]]})

    def test_filtros_busqueda_y_estadisticas_con_vencidas(self) -> None:
        ayer = (date.today() - timedelta(days=2)).strftime("%Y-%m-%d")
        manana = (date.today() + timedelta(days=2)).strftime("%Y-%m-%d")

        t_vencida = self.gestor.crear_tarea(
            titulo="Entregar informe preliminar",
            descripcion="Documento de arquitectura",
            prioridad="alta",
            estado="pendiente",
            fecha_limite=ayer,
            etiquetas=["doc", "urgente"],
        )
        t_activa = self.gestor.crear_tarea(
            titulo="Desarrollar frontend",
            descripcion="Interfaz moderna en español",
            prioridad="media",
            estado="en_progreso",
            fecha_limite=manana,
            etiquetas=["web"],
        )
        t_completada_pasada = self.gestor.crear_tarea(
            titulo="Definir requerimientos",
            prioridad="baja",
            estado="completada",
            fecha_limite=ayer,
        )

        # Filtrar por estado
        pendientes = self.gestor.listar_tareas(estado="pendiente")
        self.assertEqual(len(pendientes), 1)
        self.assertEqual(pendientes[0]["id"], t_vencida["id"])

        # Filtrar por prioridad
        altas = self.gestor.listar_tareas(prioridad="alta")
        self.assertEqual(len(altas), 1)
        self.assertEqual(altas[0]["id"], t_vencida["id"])

        # Buscar por texto
        busqueda = self.gestor.listar_tareas(busqueda="arquitectura")
        self.assertEqual(len(busqueda), 1)
        self.assertEqual(busqueda[0]["id"], t_vencida["id"])

        # Estadísticas y conteo de vencidas (las completadas no cuentan como vencidas)
        stats = self.gestor.obtener_estadisticas()
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["pendientes"], 1)
        self.assertEqual(stats["en_progreso"], 1)
        self.assertEqual(stats["completadas"], 1)
        self.assertEqual(stats["vencidas"], 1)

        # Eliminar tarea
        self.gestor.eliminar_tarea(t_activa["id"])
        with self.assertRaises(ErrorTareaNoEncontrada):
            self.gestor.obtener_tarea(t_activa["id"])


class TestServidorHTTPIntegracion(unittest.TestCase):
    """Pruebas de integración sobre la API HTTP y el servidor Web."""

    def setUp(self) -> None:
        os.environ["SILENCIAR_LOGS_HTTP"] = "1"
        self.temp_dir = tempfile.TemporaryDirectory()
        self.ruta_json = Path(self.temp_dir.name) / "api_tareas.json"
        self.servidor, self.gestor = crear_servidor(
            host="127.0.0.1",
            puerto=0,
            ruta_archivo=self.ruta_json,
        )
        self.puerto = self.servidor.server_address[1]
        self.url_base = f"http://127.0.0.1:{self.puerto}"
        self.hilo = threading.Thread(target=self.servidor.serve_forever, daemon=True)
        self.hilo.start()

    def tearDown(self) -> None:
        self.servidor.shutdown()
        self.servidor.server_close()
        self.temp_dir.cleanup()

    def _peticion(self, metodo: str, ruta: str, cuerpo: dict | None = None) -> tuple[int, dict]:
        datos = json.dumps(cuerpo).encode("utf-8") if cuerpo is not None else None
        req = Request(
            f"{self.url_base}{ruta}",
            data=datos,
            method=metodo,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urlopen(req) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except HTTPError as err:
            try:
                contenido = err.read().decode("utf-8")
                return err.code, json.loads(contenido)
            finally:
                err.close()

    def test_flujo_completo_api_y_panel_web(self) -> None:
        # 1. Verificar que el panel HTML carga en /
        with urlopen(f"{self.url_base}/") as resp:
            html = resp.read().decode("utf-8")
            self.assertEqual(resp.status, 200)
            self.assertIn("Lista de Tareas", html)

        # 2. Crear tarea previa A y tarea dependiente B
        codigo_a, resp_a = self._peticion(
            "POST",
            "/api/tareas",
            {
                "titulo": "Preparar entorno",
                "prioridad": "alta",
                "estado": "pendiente",
                "fecha_limite": "2020-01-01",
                "etiquetas": ["infra"],
            },
        )
        self.assertEqual(codigo_a, 201)
        id_a = resp_a["tarea"]["id"]

        codigo_b, resp_b = self._peticion(
            "POST",
            "/api/tareas",
            {
                "titulo": "Desplegar servicio",
                "prioridad": "media",
                "estado": "pendiente",
                "dependencias": [id_a],
            },
        )
        self.assertEqual(codigo_b, 201)
        id_b = resp_b["tarea"]["id"]

        # 3. Intentar completar B antes que A debe ser bloqueado (HTTP 400)
        cod_bloq, resp_bloq = self._peticion("POST", f"/api/tareas/{id_b}/completar")
        self.assertEqual(cod_bloq, 400)
        self.assertEqual(resp_bloq["codigo"], "TAREA_BLOQUEADA")

        # 4. Intentar crear dependencia circular A -> B debe ser bloqueado (HTTP 400)
        cod_circ, resp_circ = self._peticion(
            "PUT",
            f"/api/tareas/{id_a}",
            {"dependencias": [id_b]},
        )
        self.assertEqual(cod_circ, 400)
        self.assertEqual(resp_circ["codigo"], "DEPENDENCIA_CIRCULAR")

        # 5. Consultar resumen estadístico (debe incluir 1 vencida y 1 bloqueada)
        cod_stats, stats = self._peticion("GET", "/api/estadisticas")
        self.assertEqual(cod_stats, 200)
        self.assertEqual(stats["vencidas"], 1)
        self.assertEqual(stats["bloqueadas"], 1)

        # 6. Completar A y luego completar B exitosamente
        cod_comp_a, _ = self._peticion("POST", f"/api/tareas/{id_a}/completar")
        self.assertEqual(cod_comp_a, 200)

        cod_comp_b, resp_comp_b = self._peticion("POST", f"/api/tareas/{id_b}/completar")
        self.assertEqual(cod_comp_b, 200)
        self.assertEqual(resp_comp_b["tarea"]["estado"], "completada")


if __name__ == "__main__":
    unittest.main()
