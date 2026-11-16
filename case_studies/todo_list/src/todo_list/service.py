"""Servicio de lógica de negocio para gestión de tareas, dependencias y KPIs."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, List, Optional, Sequence

from todo_list.models import (
    CyclicDependencyError,
    DependencyNotCompletedError,
    InvalidDependencyError,
    Priority,
    Task,
    TaskNotFoundError,
    TaskStatus,
    TaskSummary,
    current_timestamp_iso,
)
from todo_list.repository import JsonTaskRepository


@dataclass
class TaskFilter:
    """Criterios de filtrado y búsqueda para el listado de tareas."""

    status: Optional[str] = None
    priority: Optional[str] = None
    tag: Optional[str] = None
    search: Optional[str] = None
    overdue_only: bool = False
    reference_date: Optional[date] = None


class TaskService:
    """Orquesta las operaciones CRUD, el grafo de dependencias y las métricas."""

    def __init__(self, repository: JsonTaskRepository) -> None:
        """Inicializa el servicio con el repositorio de persistencia inyectado.

        Args:
            repository: Instancia de JsonTaskRepository.
        """
        self._repository = repository

    @property
    def repository(self) -> JsonTaskRepository:
        """Retorna el repositorio subyacente."""
        return self._repository

    def create_task(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        title: str,
        description: str = "",
        priority: str | Priority = Priority.MEDIA,
        status: str | TaskStatus = TaskStatus.PENDIENTE,
        due_date: Optional[str] = None,
        tags: Optional[Sequence[str]] = None,
        dependencies: Optional[Sequence[str]] = None,
        task_id: Optional[str] = None,
    ) -> Task:
        """Crea una nueva tarea validando sus campos, dependencias y estado.

        Args:
            title: Título obligatorio de la tarea.
            description: Descripción opcional.
            priority: Nivel de prioridad ('baja', 'media', 'alta').
            status: Estado inicial ('pendiente', 'en_progreso', 'completada').
            due_date: Fecha límite opcional en formato YYYY-MM-DD.
            tags: Lista opcional de etiquetas.
            dependencies: Lista opcional de IDs de tareas previas.
            task_id: Identificador explícito opcional (UUID4 por defecto).

        Returns:
            La instancia de Task creada y persistida.
        """
        tasks = self._repository.list_all()
        tasks_by_id: Dict[str, Task] = {item.id: item for item in tasks}

        assigned_id = (task_id.strip() if task_id else "") or str(uuid.uuid4())
        if assigned_id in tasks_by_id:
            raise InvalidDependencyError(
                f"Ya existe una tarea con el identificador '{assigned_id}'."
            )

        new_task = Task(
            id=assigned_id,
            title=title,
            description=description,
            priority=Priority.from_value(priority),
            status=TaskStatus.from_value(status),
            due_date=due_date,
            tags=list(tags or []),
            dependencies=list(dependencies or []),
        )

        candidate_map = dict(tasks_by_id)
        candidate_map[new_task.id] = new_task
        self._validate_dependencies_and_cycles(new_task, candidate_map)
        self._validate_completion_constraints(new_task, candidate_map)

        tasks.append(new_task)
        self._repository.save_all(tasks)
        return new_task

    def get_task(self, task_id: str) -> Task:
        """Obtiene una tarea existente por su ID.

        Args:
            task_id: Identificador único de la tarea.

        Returns:
            La instancia de Task encontrada.

        Raises:
            TaskNotFoundError: Si la tarea no existe.
        """
        task = self._repository.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(f"No se encontró la tarea con ID '{task_id}'.")
        return task

    def update_task(self, task_id: str, **changes: Any) -> Task:
        """Actualiza los campos de una tarea existente validando invariantes.

        Args:
            task_id: Identificador de la tarea a modificar.
            **changes: Campos a actualizar (title, description, priority, status,
                due_date, tags, dependencies).

        Returns:
            La tarea actualizada y persistida.
        """
        tasks = self._repository.list_all()
        tasks_by_id: Dict[str, Task] = {item.id: item for item in tasks}
        if task_id not in tasks_by_id:
            raise TaskNotFoundError(f"No se encontró la tarea con ID '{task_id}'.")

        current = tasks_by_id[task_id]
        updated_task = Task(
            id=current.id,
            title=changes.get("title", current.title),
            description=(
                changes["description"]
                if "description" in changes
                else current.description
            ),
            priority=changes.get("priority", current.priority),
            status=changes.get("status", current.status),
            due_date=(
                changes["due_date"] if "due_date" in changes else current.due_date
            ),
            tags=changes["tags"] if "tags" in changes else current.tags,
            dependencies=(
                changes["dependencies"]
                if "dependencies" in changes
                else current.dependencies
            ),
            created_at=current.created_at,
            updated_at=current_timestamp_iso(),
        )

        candidate_map = dict(tasks_by_id)
        candidate_map[task_id] = updated_task
        self._validate_dependencies_and_cycles(updated_task, candidate_map)
        self._validate_completion_constraints(updated_task, candidate_map)
        self._validate_dependents_consistency(updated_task, candidate_map)

        for idx, item in enumerate(tasks):
            if item.id == task_id:
                tasks[idx] = updated_task
                break
        self._repository.save_all(tasks)
        return updated_task

    def update_status(self, task_id: str, new_status: str | TaskStatus) -> Task:
        """Cambia el estado de una tarea verificando reglas de bloqueo.

        Args:
            task_id: Identificador de la tarea.
            new_status: Nuevo estado deseado.

        Returns:
            La tarea actualizada.
        """
        return self.update_task(task_id, status=new_status)

    def complete_task(self, task_id: str) -> Task:
        """Marca una tarea como completada si sus dependencias lo permiten.

        Args:
            task_id: Identificador de la tarea a completar.

        Returns:
            La tarea en estado completada.
        """
        return self.update_status(task_id, TaskStatus.COMPLETADA)

    def delete_task(self, task_id: str) -> None:
        """Elimina una tarea y limpia su ID de las dependencias de otras tareas.

        Args:
            task_id: Identificador de la tarea a eliminar.

        Raises:
            TaskNotFoundError: Si la tarea no existe.
        """
        tasks = self._repository.list_all()
        if not any(task.id == task_id for task in tasks):
            raise TaskNotFoundError(f"No se encontró la tarea con ID '{task_id}'.")

        remaining: List[Task] = []
        for task in tasks:
            if task.id == task_id:
                continue
            if task_id in task.dependencies:
                cleaned_deps = [dep for dep in task.dependencies if dep != task_id]
                task = Task(
                    id=task.id,
                    title=task.title,
                    description=task.description,
                    priority=task.priority,
                    status=task.status,
                    due_date=task.due_date,
                    tags=task.tags,
                    dependencies=cleaned_deps,
                    created_at=task.created_at,
                    updated_at=current_timestamp_iso(),
                )
            remaining.append(task)

        self._repository.save_all(remaining)

    def list_tasks(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
        overdue_only: bool = False,
        reference_date: Optional[date] = None,
        filters: Optional[TaskFilter] = None,
    ) -> List[Task]:
        """Lista las tareas aplicando filtros combinables y búsqueda por texto.

        Args:
            status: Filtra por estado ('pendiente', 'en_progreso', 'completada').
            priority: Filtra por prioridad ('baja', 'media', 'alta').
            tag: Filtra por etiqueta exacta (insensible a mayúsculas).
            search: Texto libre a buscar en título, descripción o etiquetas.
            overdue_only: Si es True, devuelve solo tareas vencidas no completadas.
            reference_date: Fecha de referencia para evaluar vencimiento.
            filters: Objeto TaskFilter opcional (tiene precedencia si se provee).

        Returns:
            Lista filtrada de instancias Task.
        """
        active = filters or TaskFilter(
            status=status,
            priority=priority,
            tag=tag,
            search=search,
            overdue_only=overdue_only,
            reference_date=reference_date,
        )
        return [
            task
            for task in self._repository.list_all()
            if self._matches_filter(task, active)
        ]

    def _matches_filter(self, task: Task, active: TaskFilter) -> bool:
        """Evalúa si una tarea satisface todos los criterios de un TaskFilter."""
        if active.status and task.status != TaskStatus.from_value(active.status):
            return False
        if active.priority and task.priority != Priority.from_value(active.priority):
            return False
        if active.tag and active.tag.strip().lower() not in task.tags:
            return False
        if active.overdue_only and not task.is_overdue(active.reference_date):
            return False
        if active.search and not self._matches_search(
            task, active.search.strip().lower()
        ):
            return False
        return True

    def get_blocking_dependencies(
        self,
        task: Task,
        tasks_by_id: Optional[Dict[str, Task]] = None,
    ) -> List[Task]:
        """Obtiene la lista de tareas previas que aún no están completadas.

        Args:
            task: Tarea cuyas dependencias se desean inspeccionar.
            tasks_by_id: Mapa opcional de tareas por ID para evitar relecturas.

        Returns:
            Lista de tareas dependencia con estado distinto de COMPLETADA.
        """
        lookup = tasks_by_id or {
            item.id: item for item in self._repository.list_all()
        }
        blocking: List[Task] = []
        for dep_id in task.dependencies:
            dep_task = lookup.get(dep_id)
            if dep_task is not None and dep_task.status != TaskStatus.COMPLETADA:
                blocking.append(dep_task)
        return blocking

    def enrich_task(
        self,
        task: Task,
        tasks_by_id: Optional[Dict[str, Task]] = None,
        reference_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Enriquece el diccionario de una tarea con estado de vencimiento y bloqueo.

        Args:
            task: Entidad Task a enriquecer.
            tasks_by_id: Mapa opcional de todas las tareas por ID.
            reference_date: Fecha de referencia opcional para cálculo de vencimiento.

        Returns:
            Diccionario serializable con metadatos de dependencias y vencimiento.
        """
        lookup = tasks_by_id or {
            item.id: item for item in self._repository.list_all()
        }
        blocking = self.get_blocking_dependencies(task, lookup)
        dependency_details = [
            {
                "id": dep_id,
                "title": lookup[dep_id].title,
                "status": lookup[dep_id].status.value,
            }
            for dep_id in task.dependencies
            if dep_id in lookup
        ]
        blocking_details = [
            {
                "id": dep.id,
                "title": dep.title,
                "status": dep.status.value,
            }
            for dep in blocking
        ]
        payload = task.to_dict()
        payload["is_overdue"] = task.is_overdue(reference_date)
        payload["is_blocked"] = (
            task.status != TaskStatus.COMPLETADA and len(blocking) > 0
        )
        payload["blocking_dependencies"] = blocking_details
        payload["dependency_details"] = dependency_details
        return payload

    def get_summary(self, reference_date: Optional[date] = None) -> TaskSummary:
        """Calcula el resumen estadístico global incluyendo tareas vencidas.

        Args:
            reference_date: Fecha de referencia opcional para evaluar vencimientos.

        Returns:
            Instancia de TaskSummary con conteos y tasas.
        """
        tasks = self._repository.list_all()
        tasks_by_id: Dict[str, Task] = {item.id: item for item in tasks}

        by_status: Dict[str, int] = {status.value: 0 for status in TaskStatus}
        by_priority: Dict[str, int] = {priority.value: 0 for priority in Priority}
        overdue_count = 0
        blocked_count = 0

        for task in tasks:
            by_status[task.status.value] += 1
            by_priority[task.priority.value] += 1
            if task.is_overdue(reference_date):
                overdue_count += 1
            if (
                task.status != TaskStatus.COMPLETADA
                and len(self.get_blocking_dependencies(task, tasks_by_id)) > 0
            ):
                blocked_count += 1

        total = len(tasks)
        completed = by_status[TaskStatus.COMPLETADA.value]
        completion_rate = round((completed / total) * 100.0, 2) if total > 0 else 0.0

        return TaskSummary(
            total=total,
            by_status=by_status,
            by_priority=by_priority,
            overdue_count=overdue_count,
            blocked_count=blocked_count,
            completion_rate=completion_rate,
        )

    @staticmethod
    def _matches_search(task: Task, query: str) -> bool:
        """Verifica si la consulta de texto coincide con título, descripción o tags."""
        if query in task.title.lower() or query in task.description.lower():
            return True
        return any(query in tag.lower() for tag in task.tags)

    @staticmethod
    def _validate_dependencies_and_cycles(
        task: Task,
        tasks_by_id: Dict[str, Task],
    ) -> None:
        """Valida existencia de dependencias y ausencia de ciclos mediante DFS.

        Args:
            task: Tarea que se está creando o actualizando.
            tasks_by_id: Grafo completo de tareas propuestas indexadas por ID.

        Raises:
            InvalidDependencyError: Si alguna dependencia no existe o es reflexiva.
            CyclicDependencyError: Si se detecta un ciclo directo o indirecto.
        """
        for dep_id in task.dependencies:
            if dep_id == task.id:
                raise InvalidDependencyError(
                    f"La tarea '{task.title}' no puede depender de sí misma."
                )
            if dep_id not in tasks_by_id:
                raise InvalidDependencyError(
                    f"La tarea dependencia con ID '{dep_id}' no existe."
                )

        state: Dict[str, int] = {}
        path: List[str] = []

        def dfs(node_id: str) -> None:
            state[node_id] = 1
            path.append(node_id)
            current_node = tasks_by_id[node_id]
            for neighbor_id in current_node.dependencies:
                neighbor_state = state.get(neighbor_id, 0)
                if neighbor_state == 1:
                    cycle_start = path.index(neighbor_id)
                    cycle_nodes = path[cycle_start:] + [neighbor_id]
                    cycle_titles = " -> ".join(
                        f"{ tasks_by_id[nid].title } ({nid})" for nid in cycle_nodes
                    )
                    raise CyclicDependencyError(
                        f"Dependencia circular detectada: {cycle_titles}."
                    )
                if neighbor_state == 0 and neighbor_id in tasks_by_id:
                    dfs(neighbor_id)
            path.pop()
            state[node_id] = 2

        for node_key in tasks_by_id:
            if state.get(node_key, 0) == 0:
                dfs(node_key)

    def _validate_completion_constraints(
        self,
        task: Task,
        tasks_by_id: Dict[str, Task],
    ) -> None:
        """Impide que una tarea figure como completada si tiene dependencias pendientes.

        Args:
            task: Tarea evaluada.
            tasks_by_id: Mapa de tareas vigentes.

        Raises:
            DependencyNotCompletedError: Si existen dependencias sin completar.
        """
        if task.status != TaskStatus.COMPLETADA:
            return
        blocking = self.get_blocking_dependencies(task, tasks_by_id)
        if blocking:
            names = ", ".join(f"'{dep.title}' ({dep.status.value})" for dep in blocking)
            blocking_ids = [dep.id for dep in blocking]
            raise DependencyNotCompletedError(
                f"No se puede completar la tarea '{task.title}' porque tiene "
                f"dependencias sin completar: {names}.",
                blocking_ids=blocking_ids,
            )

    @staticmethod
    def _validate_dependents_consistency(
        task: Task,
        tasks_by_id: Dict[str, Task],
    ) -> None:
        """Impide reabrir una tarea si otra tarea que depende de ella ya está completada.

        Args:
            task: Tarea actualizada.
            tasks_by_id: Mapa de tareas vigentes.

        Raises:
            DependencyNotCompletedError: Si una tarea dependiente ya está completada.
        """
        if task.status == TaskStatus.COMPLETADA:
            return
        completed_dependents = [
            other
            for other in tasks_by_id.values()
            if task.id in other.dependencies and other.status == TaskStatus.COMPLETADA
        ]
        if completed_dependents:
            names = ", ".join(f"'{dep.title}'" for dep in completed_dependents)
            blocking_ids = [dep.id for dep in completed_dependents]
            raise DependencyNotCompletedError(
                f"No se puede cambiar '{task.title}' a '{task.status.value}' porque "
                f"las siguientes tareas completadas dependen de ella: {names}.",
                blocking_ids=blocking_ids,
            )
