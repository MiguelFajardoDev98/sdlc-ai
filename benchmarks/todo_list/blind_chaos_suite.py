#!/usr/bin/env python3
"""Batería Ciega de Aceptación y Caos (Golden Chaos Suite) para el Benchmark To-Do List.

Evalúa de manera independiente y bajo las mismas 10 pruebas (5 funcionales + 5 de caos/frontera)
la implementación de la Sesión A (Línea Base / Sin Arnés) frente a la Sesión B (Marco SDLC-AI).
"""

from __future__ import annotations

import json
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List

ROOT_DIR = Path(__file__).resolve().parents[2]
SESION_A_DIR = ROOT_DIR / "benchmarks" / "todo_list" / "sesion_a_baseline"
SESION_B_SRC = ROOT_DIR / "case_studies" / "todo_list" / "src"

sys.path.insert(0, str(SESION_A_DIR))
sys.path.insert(0, str(SESION_B_SRC))

import gestor_tareas as mod_a  # type: ignore  # pylint: disable=wrong-import-position,import-error
from todo_list.models import TodoError  # type: ignore  # pylint: disable=wrong-import-position,import-error
from todo_list.repository import JsonTaskRepository  # type: ignore  # pylint: disable=wrong-import-position,import-error
from todo_list.service import TaskService  # type: ignore  # pylint: disable=wrong-import-position,import-error


def _make_service_b(json_path: Path) -> TaskService:
    """Crea una instancia del servicio de la Sesión B."""
    return TaskService(JsonTaskRepository(json_path))


def run_suite_sesion_a() -> List[Dict[str, Any]]:
    """Ejecuta los 10 casos de prueba sobre la Sesión A (Línea Base)."""
    results: List[Dict[str, Any]] = []
    yesterday = (date.today() - timedelta(days=2)).strftime("%Y-%m-%d")
    tomorrow = (date.today() + timedelta(days=2)).strftime("%Y-%m-%d")

    def check(tc_id: str, name: str, category: str, fn: Callable[[], None]) -> None:
        try:
            fn()
            results.append({"id": tc_id, "name": name, "category": category, "passed": True, "detail": "OK"})
        except Exception as exc:  # pylint: disable=broad-exception-caught
            results.append({"id": tc_id, "name": name, "category": category, "passed": False, "detail": f"{type(exc).__name__}: {exc}"})

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        # TC-01: Creación y persistencia JSON
        def tc01() -> None:
            db = tmp_path / "tc01.json"
            g = mod_a.GestorTareas(db)
            t = g.crear_tarea("Diseñar API", "Detalle", "alta", "pendiente", tomorrow, ["backend", "api"])
            g2 = mod_a.GestorTareas(db)
            cargada = g2.obtener_tarea(t["id"])
            assert cargada["titulo"] == "Diseñar API"
            assert cargada["prioridad"] == "alta"

        check("TC-01", "Creación y persistencia JSON", "Funcional", tc01)

        # TC-02: Filtros y búsqueda textual
        def tc02() -> None:
            db = tmp_path / "tc02.json"
            g = mod_a.GestorTareas(db)
            g.crear_tarea("Configurar Postgres", prioridad="alta", estado="pendiente", etiquetas=["db"])
            g.crear_tarea("Maquetar CSS", prioridad="baja", estado="completada", etiquetas=["ui"])
            res = g.listar_tareas(estado="pendiente", prioridad="alta", busqueda="Postgres")
            assert len(res) == 1 and res[0]["titulo"] == "Configurar Postgres"

        check("TC-02", "Filtrado multicriterio y búsqueda", "Funcional", tc02)

        # TC-03: Bloqueo de completado por dependencia pendiente
        def tc03() -> None:
            db = tmp_path / "tc03.json"
            g = mod_a.GestorTareas(db)
            t1 = g.crear_tarea("Base de datos")
            t2 = g.crear_tarea("Migraciones", dependencias=[t1["id"]])
            try:
                g.completar_tarea(t2["id"])
                raise AssertionError("Permitió completar tarea con dependencia pendiente")
            except mod_a.ErrorTareaBloqueada:
                pass

        check("TC-03", "Bloqueo de completado con dependencia pendiente", "Funcional", tc03)

        # TC-04: Limpieza de referencias al eliminar tarea previa
        def tc04() -> None:
            db = tmp_path / "tc04.json"
            g = mod_a.GestorTareas(db)
            t1 = g.crear_tarea("Tarea A")
            t2 = g.crear_tarea("Tarea B", dependencias=[t1["id"]])
            g.eliminar_tarea(t1["id"])
            actualizada = g.obtener_tarea(t2["id"])
            assert t1["id"] not in actualizada["dependencias"]

        check("TC-04", "Limpieza de dependencias huérfanas al eliminar", "Funcional", tc04)

        # TC-05: Cálculo de resumen estadístico y tareas vencidas
        def tc05() -> None:
            db = tmp_path / "tc05.json"
            g = mod_a.GestorTareas(db)
            g.crear_tarea("Vencida 1", estado="pendiente", fecha_limite=yesterday)
            g.crear_tarea("Completada pasada", estado="completada", fecha_limite=yesterday)
            g.crear_tarea("Futura", estado="pendiente", fecha_limite=tomorrow)
            stats = g.obtener_estadisticas()
            assert stats["total"] == 3
            assert stats["vencidas"] == 1

        check("TC-05", "Resumen estadístico y conteo de vencidas", "Funcional", tc05)

        # TC-06: Detección de ciclo transitivo A -> B -> C -> A
        def tc06() -> None:
            db = tmp_path / "tc06.json"
            g = mod_a.GestorTareas(db)
            ta = g.crear_tarea("Nodo A")
            tb = g.crear_tarea("Nodo B", dependencias=[ta["id"]])
            tc = g.crear_tarea("Nodo C", dependencias=[tb["id"]])
            try:
                g.actualizar_tarea(ta["id"], {"dependencias": [tc["id"]]})
                raise AssertionError("No detectó ciclo transitivo A -> B -> C -> A")
            except mod_a.ErrorDependenciaCircular:
                pass

        check("TC-06", "Detección de ciclo transitivo (A -> B -> C -> A)", "Caos/Frontera", tc06)

        # TC-07: Rechazo de fecha inválida de calendario y título vacío
        def tc07() -> None:
            db = tmp_path / "tc07.json"
            g = mod_a.GestorTareas(db)
            try:
                g.crear_tarea("   ")
                raise AssertionError("Aceptó título vacío")
            except mod_a.ErrorValidacionTarea:
                pass
            try:
                g.crear_tarea("Fecha falsa", fecha_limite="2026-02-30")
                raise AssertionError("Aceptó fecha 2026-02-30")
            except mod_a.ErrorValidacionTarea:
                pass

        check("TC-07", "Rechazo de fecha calendario inválida y título vacío", "Caos/Frontera", tc07)

        # TC-08: Resiliencia ante archivo JSON corrupto en disco
        def tc08() -> None:
            db = tmp_path / "tc08_corrupt.json"
            db.write_text("{corrupted_json: [1, 2", encoding="utf-8")
            g = mod_a.GestorTareas(db)
            assert g.listar_tareas() == []

        check("TC-08", "Recuperación automática ante archivo JSON corrupto", "Caos/Frontera", tc08)

        # TC-09: Invariante de consistencia al reabrir tarea padre de tarea ya completada
        def tc09() -> None:
            db = tmp_path / "tc09.json"
            g = mod_a.GestorTareas(db)
            ta = g.crear_tarea("Prerrequisito A")
            tb = g.crear_tarea("Dependiente B", dependencias=[ta["id"]])
            g.completar_tarea(ta["id"])
            g.completar_tarea(tb["id"])
            try:
                g.cambiar_estado(ta["id"], "pendiente")
                raise AssertionError(
                    "Permitió reabrir tarea padre 'A' a pendiente dejando a la hija 'B' completada en estado inconsistente"
                )
            except mod_a.ErrorValidacionTarea:
                pass

        check("TC-09", "Bloqueo de reapertura de prerrequisito con dependiente completada", "Caos/Frontera", tc09)

        # TC-10: Sanitización estricta de tipos no-string y límite de longitud en título
        def tc10() -> None:
            db = tmp_path / "tc10.json"
            g = mod_a.GestorTareas(db)
            try:
                g.crear_tarea("X" * 500)
                raise AssertionError("Aceptó título de 500 caracteres sin límite de longitud")
            except mod_a.ErrorValidacionTarea:
                pass

        check("TC-10", "Validación de longitud máxima y tipos estrictos en título", "Caos/Frontera", tc10)

    return results


def run_suite_sesion_b() -> List[Dict[str, Any]]:
    """Ejecuta los 10 casos de prueba sobre la Sesión B (Marco SDLC-AI)."""
    results: List[Dict[str, Any]] = []
    yesterday = (date.today() - timedelta(days=2)).strftime("%Y-%m-%d")
    tomorrow = (date.today() + timedelta(days=2)).strftime("%Y-%m-%d")

    def check(tc_id: str, name: str, category: str, fn: Callable[[], None]) -> None:
        try:
            fn()
            results.append({"id": tc_id, "name": name, "category": category, "passed": True, "detail": "OK"})
        except Exception as exc:  # pylint: disable=broad-exception-caught
            results.append({"id": tc_id, "name": name, "category": category, "passed": False, "detail": f"{type(exc).__name__}: {exc}"})

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        # TC-01
        def tc01() -> None:
            db = tmp_path / "tc01.json"
            s = _make_service_b(db)
            t = s.create_task("Diseñar API", "Detalle", "alta", "pendiente", tomorrow, ["backend", "api"])
            s2 = _make_service_b(db)
            cargada = s2.get_task(t.id)
            assert cargada.title == "Diseñar API"
            assert cargada.priority.value == "alta"

        check("TC-01", "Creación y persistencia JSON", "Funcional", tc01)

        # TC-02
        def tc02() -> None:
            db = tmp_path / "tc02.json"
            s = _make_service_b(db)
            s.create_task("Configurar Postgres", priority="alta", status="pendiente", tags=["db"])
            s.create_task("Maquetar CSS", priority="baja", status="completada", tags=["ui"])
            res = s.list_tasks(status="pendiente", priority="alta", search="Postgres")
            assert len(res) == 1 and res[0].title == "Configurar Postgres"

        check("TC-02", "Filtrado multicriterio y búsqueda", "Funcional", tc02)

        # TC-03
        def tc03() -> None:
            db = tmp_path / "tc03.json"
            s = _make_service_b(db)
            t1 = s.create_task("Base de datos")
            t2 = s.create_task("Migraciones", dependencies=[t1.id])
            try:
                s.complete_task(t2.id)
                raise AssertionError("Permitió completar tarea con dependencia pendiente")
            except TodoError:
                pass

        check("TC-03", "Bloqueo de completado con dependencia pendiente", "Funcional", tc03)

        # TC-04
        def tc04() -> None:
            db = tmp_path / "tc04.json"
            s = _make_service_b(db)
            t1 = s.create_task("Tarea A")
            t2 = s.create_task("Tarea B", dependencies=[t1.id])
            s.delete_task(t1.id)
            actualizada = s.get_task(t2.id)
            assert t1.id not in actualizada.dependencies

        check("TC-04", "Limpieza de dependencias huérfanas al eliminar", "Funcional", tc04)

        # TC-05
        def tc05() -> None:
            db = tmp_path / "tc05.json"
            s = _make_service_b(db)
            s.create_task("Vencida 1", status="pendiente", due_date=yesterday)
            s.create_task("Completada pasada", status="completada", due_date=yesterday)
            s.create_task("Futura", status="pendiente", due_date=tomorrow)
            summary = s.get_summary()
            assert summary.total == 3
            assert summary.overdue_count == 1

        check("TC-05", "Resumen estadístico y conteo de vencidas", "Funcional", tc05)

        # TC-06
        def tc06() -> None:
            db = tmp_path / "tc06.json"
            s = _make_service_b(db)
            ta = s.create_task("Nodo A")
            tb = s.create_task("Nodo B", dependencies=[ta.id])
            tc = s.create_task("Nodo C", dependencies=[tb.id])
            try:
                s.update_task(ta.id, dependencies=[tc.id])
                raise AssertionError("No detectó ciclo transitivo A -> B -> C -> A")
            except TodoError:
                pass

        check("TC-06", "Detección de ciclo transitivo (A -> B -> C -> A)", "Caos/Frontera", tc06)

        # TC-07
        def tc07() -> None:
            db = tmp_path / "tc07.json"
            s = _make_service_b(db)
            try:
                s.create_task("   ")
                raise AssertionError("Aceptó título vacío")
            except TodoError:
                pass
            try:
                s.create_task("Fecha falsa", due_date="2026-02-30")
                raise AssertionError("Aceptó fecha 2026-02-30")
            except TodoError:
                pass

        check("TC-07", "Rechazo de fecha calendario inválida y título vacío", "Caos/Frontera", tc07)

        # TC-08
        def tc08() -> None:
            db = tmp_path / "tc08_corrupt.json"
            db.write_text("{corrupted_json: [1, 2", encoding="utf-8")
            s = _make_service_b(db)
            assert s.list_tasks() == []

        check("TC-08", "Recuperación automática ante archivo JSON corrupto", "Caos/Frontera", tc08)

        # TC-09
        def tc09() -> None:
            db = tmp_path / "tc09.json"
            s = _make_service_b(db)
            ta = s.create_task("Prerrequisito A")
            tb = s.create_task("Dependiente B", dependencies=[ta.id])
            s.complete_task(ta.id)
            s.complete_task(tb.id)
            try:
                s.update_status(ta.id, "pendiente")
                raise AssertionError(
                    "Permitió reabrir tarea padre 'A' a pendiente dejando a la hija 'B' completada"
                )
            except TodoError:
                pass

        check("TC-09", "Bloqueo de reapertura de prerrequisito con dependiente completada", "Caos/Frontera", tc09)

        # TC-10
        def tc10() -> None:
            db = tmp_path / "tc10.json"
            s = _make_service_b(db)
            try:
                s.create_task("X" * 500)
                raise AssertionError("Aceptó título de 500 caracteres sin límite de longitud")
            except TodoError:
                pass

        check("TC-10", "Validación de longitud máxima y tipos estrictos en título", "Caos/Frontera", tc10)

    return results


def main() -> None:
    """Ejecuta ambas suites y muestra el resultado comparativo."""
    res_a = run_suite_sesion_a()
    res_b = run_suite_sesion_b()

    passed_a = sum(1 for r in res_a if r["passed"])
    passed_b = sum(1 for r in res_b if r["passed"])

    print("=" * 80)
    print(f"RESULTADO BATERÍA CIEGA DE CAOS (10 PRUEBAS):")
    print(f"  - Sesión A (Línea Base / Sin Arnés): {passed_a}/10 ({passed_a * 10}%)")
    print(f"  - Sesión B (Marco SDLC-AI)         : {passed_b}/10 ({passed_b * 10}%)")
    print("=" * 80)
    for ra, rb in zip(res_a, res_b):
        status_a = "PASS" if ra["passed"] else f"FAIL ({ra['detail']})"
        status_b = "PASS" if rb["passed"] else f"FAIL ({rb['detail']})"
        print(f"[{ra['id']}] ({ra['category']}) {ra['name']}")
        print(f"   Sesión A: {status_a}")
        print(f"   Sesión B: {status_b}")

    output_path = ROOT_DIR / "benchmarks" / "todo_list" / "blind_chaos_results.json"
    output_path.write_text(
        json.dumps(
            {
                "sesion_a_baseline": {"passed": passed_a, "total": 10, "results": res_a},
                "sesion_b_sdlc_ai": {"passed": passed_b, "total": 10, "results": res_b},
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
