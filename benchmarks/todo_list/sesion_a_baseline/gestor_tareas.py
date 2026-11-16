"""
Módulo de lógica de negocio y persistencia en JSON para la Lista de Tareas (To-Do List).
Utiliza exclusivamente la librería estándar de Python.
"""

from __future__ import annotations

import json
import os
import threading
import uuid
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


PRIORIDADES_VALIDAS = ("baja", "media", "alta")
ESTADOS_VALIDOS = ("pendiente", "en_progreso", "completada")


class ErrorValidacionTarea(ValueError):
    """Excepción lanzada ante errores de validación o reglas de negocio."""
    pass


class ErrorDependenciaCircular(ErrorValidacionTarea):
    """Excepción lanzada cuando se detecta una dependencia circular entre tareas."""
    pass


class ErrorTareaBloqueada(ErrorValidacionTarea):
    """Excepción lanzada cuando se intenta completar una tarea con dependencias pendientes."""
    pass


class ErrorTareaNoEncontrada(KeyError):
    """Excepción lanzada cuando no existe una tarea con el ID solicitado."""
    pass


def validar_fecha(fecha_str: Optional[str]) -> Optional[str]:
    """Valida que la fecha tenga el formato exacto YYYY-MM-DD."""
    if fecha_str is None or str(fecha_str).strip() == "":
        return None
    texto = str(fecha_str).strip()
    try:
        dt = datetime.strptime(texto, "%Y-%m-%d").date()
        return dt.strftime("%Y-%m-%d")
    except ValueError as exc:
        raise ErrorValidacionTarea(
            f"La fecha límite '{texto}' no es válida. Debe tener el formato YYYY-MM-DD."
        ) from exc


def normalizar_etiquetas(etiquetas: Any) -> List[str]:
    """Normaliza una lista o cadena separada por comas de etiquetas únicas sin vacíos."""
    if etiquetas is None:
        return []
    if isinstance(etiquetas, str):
        partes = [e.strip() for e in etiquetas.split(",")]
    elif isinstance(etiquetas, (list, tuple, set)):
        partes = [str(e).strip() for e in etiquetas]
    else:
        raise ErrorValidacionTarea("El campo 'etiquetas' debe ser una lista de textos o cadena separada por comas.")

    resultado: List[str] = []
    vistos: Set[str] = set()
    for p in partes:
        if p and p.lower() not in vistos:
            vistos.add(p.lower())
            resultado.append(p)
    return resultado


def normalizar_dependencias(dependencias: Any) -> List[str]:
    """Normaliza la lista de IDs de tareas de las que depende una tarea."""
    if dependencias is None:
        return []
    if isinstance(dependencias, str):
        partes = [d.strip() for d in dependencias.split(",") if d.strip()]
    elif isinstance(dependencias, (list, tuple, set)):
        partes = [str(d).strip() for d in dependencias if str(d).strip()]
    else:
        raise ErrorValidacionTarea("El campo 'dependencias' debe ser una lista de IDs de tareas.")

    resultado: List[str] = []
    vistos: Set[str] = set()
    for dep_id in partes:
        if dep_id not in vistos:
            vistos.add(dep_id)
            resultado.append(dep_id)
    return resultado


@dataclass
class Tarea:
    """Representa una tarea dentro de la aplicación To-Do List."""

    id: str
    titulo: str
    descripcion: str = ""
    prioridad: str = "media"
    estado: str = "pendiente"
    fecha_limite: Optional[str] = None
    etiquetas: List[str] = field(default_factory=list)
    dependencias: List[str] = field(default_factory=list)
    fecha_creacion: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    fecha_actualizacion: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def validar(self) -> None:
        """Valida la integridad de los campos individuales de la tarea."""
        if not self.titulo or not str(self.titulo).strip():
            raise ErrorValidacionTarea("El título de la tarea es obligatorio.")
        self.titulo = str(self.titulo).strip()
        self.descripcion = "" if self.descripcion is None else str(self.descripcion).strip()

        prioridad_norm = str(self.prioridad).strip().lower()
        if prioridad_norm not in PRIORIDADES_VALIDAS:
            raise ErrorValidacionTarea(
                f"Prioridad '{self.prioridad}' no válida. Valores permitidos: {', '.join(PRIORIDADES_VALIDAS)}."
            )
        self.prioridad = prioridad_norm

        estado_norm = str(self.estado).strip().lower()
        if estado_norm not in ESTADOS_VALIDOS:
            raise ErrorValidacionTarea(
                f"Estado '{self.estado}' no válido. Valores permitidos: {', '.join(ESTADOS_VALIDOS)}."
            )
        self.estado = estado_norm

        self.fecha_limite = validar_fecha(self.fecha_limite)
        self.etiquetas = normalizar_etiquetas(self.etiquetas)
        self.dependencias = normalizar_dependencias(self.dependencias)

    def esta_vencida(self, fecha_referencia: Optional[date] = None) -> bool:
        """Indica si la tarea tiene fecha límite anterior a hoy y aún no está completada."""
        if self.estado == "completada" or not self.fecha_limite:
            return False
        hoy = fecha_referencia or date.today()
        try:
            limite = datetime.strptime(self.fecha_limite, "%Y-%m-%d").date()
            return limite < hoy
        except ValueError:
            return False

    def a_diccionario(self, fecha_referencia: Optional[date] = None) -> Dict[str, Any]:
        """Serializa la tarea a un diccionario compatible con JSON incluyendo metadatos calculados."""
        datos = asdict(self)
        datos["vencida"] = self.esta_vencida(fecha_referencia)
        return datos

    @classmethod
    def desde_diccionario(cls, datos: Dict[str, Any]) -> "Tarea":
        """Reconstruye una instancia de Tarea desde un diccionario."""
        tarea = cls(
            id=str(datos.get("id") or uuid.uuid4().hex[:8]),
            titulo=datos.get("titulo", ""),
            descripcion=datos.get("descripcion", "") or "",
            prioridad=datos.get("prioridad", "media"),
            estado=datos.get("estado", "pendiente"),
            fecha_limite=datos.get("fecha_limite"),
            etiquetas=datos.get("etiquetas", []),
            dependencias=datos.get("dependencias", []),
            fecha_creacion=datos.get("fecha_creacion") or datetime.now().isoformat(timespec="seconds"),
            fecha_actualizacion=datos.get("fecha_actualizacion") or datetime.now().isoformat(timespec="seconds"),
        )
        tarea.validar()
        return tarea


class GestorTareas:
    """
    Gestiona el ciclo de vida de las tareas, validaciones de dependencias,
    búsqueda/filtrado, estadísticas y persistencia atómica en archivo JSON.
    """

    def __init__(self, ruta_archivo: str | Path = "tareas.json") -> None:
        self.ruta_archivo = Path(ruta_archivo)
        self._lock = threading.RLock()
        self._tareas: Dict[str, Tarea] = {}
        self.cargar()

    def cargar(self) -> None:
        """Carga las tareas desde el archivo JSON si existe; si no, inicializa vacío."""
        with self._lock:
            if not self.ruta_archivo.exists():
                self._tareas = {}
                self.guardar()
                return

            try:
                contenido = self.ruta_archivo.read_text(encoding="utf-8").strip()
                if not contenido:
                    self._tareas = {}
                    return
                datos = json.loads(contenido)
                lista_tareas = datos.get("tareas", datos) if isinstance(datos, dict) else datos
                if not isinstance(lista_tareas, list):
                    raise ValueError("Formato de archivo JSON inválido: se esperaba una lista de tareas.")
                cargadas: Dict[str, Tarea] = {}
                for item in lista_tareas:
                    tarea = Tarea.desde_diccionario(item)
                    cargadas[tarea.id] = tarea
                self._tareas = cargadas
            except Exception as exc:
                raise RuntimeError(f"Error al cargar el archivo de tareas '{self.ruta_archivo}': {exc}") from exc

    def guardar(self) -> None:
        """Guarda de forma segura (mediante archivo temporal) todas las tareas en formato JSON."""
        with self._lock:
            self.ruta_archivo.parent.mkdir(parents=True, exist_ok=True)
            datos_Persistir = {
                "actualizado_en": datetime.now().isoformat(timespec="seconds"),
                "tareas": [
                    {
                        "id": t.id,
                        "titulo": t.titulo,
                        "descripcion": t.descripcion,
                        "prioridad": t.prioridad,
                        "estado": t.estado,
                        "fecha_limite": t.fecha_limite,
                        "etiquetas": t.etiquetas,
                        "dependencias": t.dependencias,
                        "fecha_creacion": t.fecha_creacion,
                        "fecha_actualizacion": t.fecha_actualizacion,
                    }
                    for t in self._tareas.values()
                ],
            }
            ruta_temp = self.ruta_archivo.with_suffix(".tmp")
            ruta_temp.write_text(
                json.dumps(datos_Persistir, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            os.replace(ruta_temp, self.ruta_archivo)

    def _generar_id_unico(self) -> str:
        """Genera un identificador corto único para una nueva tarea."""
        while True:
            nuevo_id = uuid.uuid4().hex[:8]
            if nuevo_id not in self._tareas:
                return nuevo_id

    def _validar_existencia_dependencias(self, tarea_id: str, dependencias: List[str]) -> None:
        """Verifica que todas las tareas de las que depende existan y no sea ella misma."""
        for dep_id in dependencias:
            if dep_id == tarea_id:
                raise ErrorDependenciaCircular(
                    f"Dependencia circular detectada: la tarea '{tarea_id}' no puede depender de sí misma."
                )
            if dep_id not in self._tareas:
                raise ErrorValidacionTarea(
                    f"La tarea previa con ID '{dep_id}' no existe."
                )

    def _verificar_sin_ciclos(self, tarea_id: str, nuevas_dependencias: List[str]) -> None:
        """
        Verifica mediante búsqueda en profundidad (DFS) que asignar `nuevas_dependencias`
        a `tarea_id` no introduzca un ciclo en el grafo de dependencias.
        """
        self._validar_existencia_dependencias(tarea_id, nuevas_dependencias)

        visitados: Set[str] = set()
        en_pila: Set[str] = {tarea_id}

        def dfs(actual_id: str, camino: List[str]) -> None:
            if actual_id in en_pila:
                ciclo_str = " -> ".join(camino + [actual_id])
                raise ErrorDependenciaCircular(
                    f"No se puede guardar la dependencia porque genera una dependencia circular ({ciclo_str})."
                )
            if actual_id in visitados:
                return

            visitados.add(actual_id)
            en_pila.add(actual_id)

            deps = nuevas_dependencias if actual_id == tarea_id else self._tareas[actual_id].dependencias
            for sig_id in deps:
                if sig_id in self._tareas or sig_id == tarea_id:
                    dfs(sig_id, camino + [actual_id])

            en_pila.remove(actual_id)

        for dep_id in nuevas_dependencias:
            dfs(dep_id, [tarea_id])

    def obtener_dependencias_incompletas(self, dependencias: List[str]) -> List[Tarea]:
        """Devuelve la lista de objetos Tarea de las dependencias que aún no están completadas."""
        incompletas: List[Tarea] = []
        for dep_id in dependencias:
            tarea_dep = self._tareas.get(dep_id)
            if tarea_dep and tarea_dep.estado != "completada":
                incompletas.append(tarea_dep)
        return incompletas

    def _validar_completado_permitido(self, dependencias: List[str]) -> None:
        """Lanza ErrorTareaBloqueada si alguna de las dependencias no está en estado 'completada'."""
        incompletas = self.obtener_dependencias_incompletas(dependencias)
        if incompletas:
            nombres = ", ".join(f"'{t.titulo}' ({t.id})" for t in incompletas)
            raise ErrorTareaBloqueada(
                f"No se puede marcar la tarea como completada porque tiene tareas previas sin completar: {nombres}."
            )

    def _enriquecer_tarea(self, tarea: Tarea, fecha_referencia: Optional[date] = None) -> Dict[str, Any]:
        """Enriquece el diccionario de la tarea con detalles de sus dependencias y estado de bloqueo."""
        datos = tarea.a_diccionario(fecha_referencia)
        incompletas = self.obtener_dependencias_incompletas(tarea.dependencias)
        datos["bloqueada"] = len(incompletas) > 0
        datos["dependencias_incompletas"] = [
            {"id": t.id, "titulo": t.titulo, "estado": t.estado}
            for t in incompletas
        ]
        datos["dependencias_detalle"] = [
            {
                "id": dep_id,
                "titulo": self._tareas[dep_id].titulo if dep_id in self._tareas else "(Eliminada)",
                "estado": self._tareas[dep_id].estado if dep_id in self._tareas else "desconocido",
                "completada": (self._tareas[dep_id].estado == "completada") if dep_id in self._tareas else False,
            }
            for dep_id in tarea.dependencias
        ]
        return datos

    def crear_tarea(
        self,
        titulo: str,
        descripcion: str = "",
        prioridad: str = "media",
        estado: str = "pendiente",
        fecha_limite: Optional[str] = None,
        etiquetas: Any = None,
        dependencias: Any = None,
        tarea_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Crea una nueva tarea validando campos, dependencias circulares y bloqueo de completado."""
        with self._lock:
            nuevo_id = str(tarea_id).strip() if tarea_id else self._generar_id_unico()
            if nuevo_id in self._tareas:
                raise ErrorValidacionTarea(f"Ya existe una tarea con el ID '{nuevo_id}'.")

            ahora = datetime.now().isoformat(timespec="seconds")
            nueva_tarea = Tarea(
                id=nuevo_id,
                titulo=titulo,
                descripcion=descripcion,
                prioridad=prioridad,
                estado=estado,
                fecha_limite=fecha_limite,
                etiquetas=etiquetas if etiquetas is not None else [],
                dependencias=dependencias if dependencias is not None else [],
                fecha_creacion=ahora,
                fecha_actualizacion=ahora,
            )
            nueva_tarea.validar()
            self._verificar_sin_ciclos(nueva_tarea.id, nueva_tarea.dependencias)

            if nueva_tarea.estado == "completada":
                self._validar_completado_permitido(nueva_tarea.dependencias)

            self._tareas[nueva_tarea.id] = nueva_tarea
            self.guardar()
            return self._enriquecer_tarea(nueva_tarea)

    def obtener_tarea(self, tarea_id: str) -> Dict[str, Any]:
        """Obtiene una tarea por su ID o lanza ErrorTareaNoEncontrada."""
        with self._lock:
            tarea = self._tareas.get(tarea_id)
            if not tarea:
                raise ErrorTareaNoEncontrada(f"No se encontró la tarea con ID '{tarea_id}'.")
            return self._enriquecer_tarea(tarea)

    def actualizar_tarea(self, tarea_id: str, cambios: Dict[str, Any]) -> Dict[str, Any]:
        """
        Actualiza los campos de una tarea existente validando:
        - Formato de los campos
        - Que no se introduzcan dependencias circulares
        - Que no pase a estado 'completada' si tiene dependencias sin completar
        - Que si tiene tareas dependientes ya completadas, no pueda reabrirse dejando inconsistencias
          (o permite actualizar manteniendo las reglas de negocio).
        """
        with self._lock:
            actual = self._tareas.get(tarea_id)
            if not actual:
                raise ErrorTareaNoEncontrada(f"No se encontró la tarea con ID '{tarea_id}'.")

            titulo = cambios.get("titulo", actual.titulo)
            descripcion = cambios.get("descripcion", actual.descripcion)
            prioridad = cambios.get("prioridad", actual.prioridad)
            estado = cambios.get("estado", actual.estado)
            fecha_limite = cambios["fecha_limite"] if "fecha_limite" in cambios else actual.fecha_limite
            etiquetas = cambios["etiquetas"] if "etiquetas" in cambios else list(actual.etiquetas)
            dependencias = cambios["dependencias"] if "dependencias" in cambios else list(actual.dependencias)

            candidata = Tarea(
                id=actual.id,
                titulo=titulo,
                descripcion=descripcion,
                prioridad=prioridad,
                estado=estado,
                fecha_limite=fecha_limite,
                etiquetas=etiquetas,
                dependencias=dependencias,
                fecha_creacion=actual.fecha_creacion,
                fecha_actualizacion=datetime.now().isoformat(timespec="seconds"),
            )
            candidata.validar()
            self._verificar_sin_ciclos(candidata.id, candidata.dependencias)

            if candidata.estado == "completada":
                self._validar_completado_permitido(candidata.dependencias)

            self._tareas[tarea_id] = candidata
            self.guardar()
            return self._enriquecer_tarea(candidata)

    def completar_tarea(self, tarea_id: str) -> Dict[str, Any]:
        """Marca una tarea como completada si todas sus tareas previas están completadas."""
        return self.actualizar_tarea(tarea_id, {"estado": "completada"})

    def cambiar_estado(self, tarea_id: str, nuevo_estado: str) -> Dict[str, Any]:
        """Cambia el estado de una tarea ('pendiente', 'en_progreso', 'completada')."""
        return self.actualizar_tarea(tarea_id, {"estado": nuevo_estado})

    def eliminar_tarea(self, tarea_id: str) -> Dict[str, Any]:
        """
        Elimina una tarea por su ID y limpia la referencia a su ID en las tareas
        que dependían de ella.
        """
        with self._lock:
            tarea = self._tareas.get(tarea_id)
            if not tarea:
                raise ErrorTareaNoEncontrada(f"No se encontró la tarea con ID '{tarea_id}'.")

            datos_eliminada = self._enriquecer_tarea(tarea)
            del self._tareas[tarea_id]

            for otra in self._tareas.values():
                if tarea_id in otra.dependencias:
                    otra.dependencias = [d for d in otra.dependencias if d != tarea_id]
                    otra.fecha_actualizacion = datetime.now().isoformat(timespec="seconds")

            self.guardar()
            return datos_eliminada

    def listar_tareas(
        self,
        estado: Optional[str] = None,
        prioridad: Optional[str] = None,
        busqueda: Optional[str] = None,
        etiqueta: Optional[str] = None,
        vencidas: Optional[bool] = None,
        fecha_referencia: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """
        Lista las tareas aplicando filtros opcionales por estado, prioridad,
        etiqueta, texto de búsqueda y condición de vencimiento.
        """
        with self._lock:
            resultado: List[Tarea] = list(self._tareas.values())

            if estado and estado.strip().lower() not in ("", "todos", "todas"):
                est_norm = estado.strip().lower()
                resultado = [t for t in resultado if t.estado == est_norm]

            if prioridad and prioridad.strip().lower() not in ("", "todas", "todos"):
                prio_norm = prioridad.strip().lower()
                resultado = [t for t in resultado if t.prioridad == prio_norm]

            if etiqueta and etiqueta.strip():
                etiq_norm = etiqueta.strip().lower()
                resultado = [
                    t for t in resultado
                    if any(e.lower() == etiq_norm for e in t.etiquetas)
                ]

            if busqueda and busqueda.strip():
                termino = busqueda.strip().lower()
                resultado = [
                    t for t in resultado
                    if termino in t.titulo.lower()
                    or termino in t.descripcion.lower()
                    or any(termino in e.lower() for e in t.etiquetas)
                    or termino in t.id.lower()
                ]

            if vencidas is not None:
                resultado = [t for t in resultado if t.esta_vencida(fecha_referencia) == vencidas]

            orden_prioridad = {"alta": 0, "media": 1, "baja": 2}
            orden_estado = {"en_progreso": 0, "pendiente": 1, "completada": 2}

            resultado.sort(
                key=lambda t: (
                    orden_estado.get(t.estado, 99),
                    t.fecha_limite if t.fecha_limite else "9999-12-31",
                    orden_prioridad.get(t.prioridad, 99),
                    t.titulo.lower(),
                )
            )

            return [self._enriquecer_tarea(t, fecha_referencia) for t in resultado]

    def obtener_estadisticas(self, fecha_referencia: Optional[date] = None) -> Dict[str, Any]:
        """
        Calcula y devuelve el resumen estadístico de todas las tareas, incluyendo
        el conteo de tareas vencidas, por estado, por prioridad y bloqueadas.
        """
        with self._lock:
            hoy = fecha_referencia or date.today()
            tareas = list(self._tareas.values())
            total = len(tareas)

            pendientes = sum(1 for t in tareas if t.estado == "pendiente")
            en_progreso = sum(1 for t in tareas if t.estado == "en_progreso")
            completadas = sum(1 for t in tareas if t.estado == "completada")
            vencidas = sum(1 for t in tareas if t.esta_vencida(hoy))
            bloqueadas = sum(
                1
                for t in tareas
                if t.estado != "completada" and len(self.obtener_dependencias_incompletas(t.dependencias)) > 0
            )

            por_prioridad = {
                "alta": sum(1 for t in tareas if t.prioridad == "alta"),
                "media": sum(1 for t in tareas if t.prioridad == "media"),
                "baja": sum(1 for t in tareas if t.prioridad == "baja"),
            }

            por_estado = {
                "pendiente": pendientes,
                "en_progreso": en_progreso,
                "completada": completadas,
            }

            etiquetas_conteo: Dict[str, int] = {}
            for t in tareas:
                for et in t.etiquetas:
                    etiquetas_conteo[et] = etiquetas_conteo.get(et, 0) + 1

            porcentaje_completado = round((completadas / total) * 100, 1) if total > 0 else 0.0

            return {
                "total": total,
                "pendientes": pendientes,
                "en_progreso": en_progreso,
                "completadas": completadas,
                "vencidas": vencidas,
                "bloqueadas": bloqueadas,
                "porcentaje_completado": porcentaje_completado,
                "por_estado": por_estado,
                "por_prioridad": por_prioridad,
                "etiquetas": etiquetas_conteo,
                "fecha_referencia": hoy.strftime("%Y-%m-%d"),
            }
