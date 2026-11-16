"""Modelos de dominio, enumeraciones y excepciones para la Lista de Tareas."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence

ISO_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MAX_TITLE_LENGTH = 200


class TodoError(Exception):
    """Excepción base de dominio para el sistema de gestión de tareas."""


class ValidationError(TodoError):
    """Se lanza cuando algún atributo de entrada incumple las reglas de dominio."""


class TaskNotFoundError(TodoError):
    """Se lanza cuando no se encuentra una tarea con el identificador indicado."""


class InvalidDependencyError(ValidationError):
    """Se lanza cuando se referencia una dependencia inexistente o reflexiva."""


class CyclicDependencyError(TodoError):
    """Se lanza cuando se detecta una dependencia circular en el grafo de tareas."""


class DependencyNotCompletedError(TodoError):
    """Se lanza al intentar completar o reabrir violando dependencias previas."""

    def __init__(
        self,
        message: str,
        blocking_ids: Optional[List[str]] = None,
    ) -> None:
        """Inicializa la excepción con los identificadores que bloquean la acción.

        Args:
            message: Descripción legible del bloqueo.
            blocking_ids: Lista de IDs de tareas que impiden completar la operación.
        """
        super().__init__(message)
        self.blocking_ids: List[str] = list(blocking_ids or [])


class Priority(str, Enum):
    """Niveles de prioridad permitidos para una tarea."""

    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"

    @classmethod
    def from_value(cls, value: str | "Priority") -> "Priority":
        """Convierte una cadena o instancia en un valor válido de Priority.

        Args:
            value: Valor de prioridad a validar.

        Returns:
            Instancia de Priority correspondiente.

        Raises:
            ValidationError: Si el valor no pertenece a {baja, media, alta}.
        """
        if isinstance(value, cls):
            return value
        if not isinstance(value, str):
            raise ValidationError("La prioridad debe ser una cadena de texto.")
        normalized = value.strip().lower()
        for item in cls:
            if item.value == normalized:
                return item
        valid = ", ".join(item.value for item in cls)
        raise ValidationError(
            f"Prioridad inválida '{value}'. Valores permitidos: {valid}."
        )


class TaskStatus(str, Enum):
    """Estados del ciclo de vida de una tarea."""

    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    COMPLETADA = "completada"

    @classmethod
    def from_value(cls, value: str | "TaskStatus") -> "TaskStatus":
        """Convierte una cadena o instancia en un valor válido de TaskStatus.

        Args:
            value: Valor de estado a validar.

        Returns:
            Instancia de TaskStatus correspondiente.

        Raises:
            ValidationError: Si el valor no pertenece a los estados válidos.
        """
        if isinstance(value, cls):
            return value
        if not isinstance(value, str):
            raise ValidationError("El estado debe ser una cadena de texto.")
        normalized = value.strip().lower()
        for item in cls:
            if item.value == normalized:
                return item
        valid = ", ".join(item.value for item in cls)
        raise ValidationError(
            f"Estado inválido '{value}'. Valores permitidos: {valid}."
        )


def current_timestamp_iso() -> str:
    """Genera una marca de tiempo UTC actual en formato ISO-8601.

    Returns:
        Cadena con timestamp ISO-8601 en UTC.
    """
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def validate_due_date(due_date: Optional[str]) -> Optional[str]:
    """Valida que la fecha límite cumpla estrictamente el formato YYYY-MM-DD.

    Args:
        due_date: Cadena de fecha opcional o None.

    Returns:
        Cadena normalizada YYYY-MM-DD o None si está vacía/nula.

    Raises:
        ValidationError: Si el formato no es YYYY-MM-DD o la fecha no existe.
    """
    if due_date is None:
        return None
    if not isinstance(due_date, str):
        raise ValidationError("La fecha límite debe ser una cadena YYYY-MM-DD.")
    cleaned = due_date.strip()
    if not cleaned:
        return None
    if not ISO_DATE_PATTERN.match(cleaned):
        raise ValidationError(
            f"Fecha límite inválida '{due_date}'. Use el formato YYYY-MM-DD."
        )
    try:
        date.fromisoformat(cleaned)
    except ValueError as exc:
        raise ValidationError(
            f"Fecha límite inexistente en el calendario: '{due_date}'."
        ) from exc
    return cleaned


def normalize_tags(tags: Optional[Sequence[str]]) -> List[str]:
    """Normaliza una secuencia de etiquetas en minúsculas y sin duplicados.

    Args:
        tags: Secuencia opcional de etiquetas.

    Returns:
        Lista depurada de etiquetas únicas.

    Raises:
        ValidationError: Si el contenedor o algún elemento no es válido.
    """
    if tags is None:
        return []
    if isinstance(tags, (str, bytes)) or not isinstance(tags, Sequence):
        raise ValidationError("Las etiquetas deben enviarse como una lista de textos.")
    result: List[str] = []
    seen: set[str] = set()
    for raw_tag in tags:
        if not isinstance(raw_tag, str):
            raise ValidationError("Cada etiqueta debe ser una cadena de texto.")
        cleaned = raw_tag.strip().lower()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            result.append(cleaned)
    return result


def normalize_dependencies(dependencies: Optional[Sequence[str]]) -> List[str]:
    """Normaliza una secuencia de IDs de dependencias eliminando duplicados.

    Args:
        dependencies: Secuencia opcional de identificadores de tareas.

    Returns:
        Lista depurada de IDs de dependencias únicos.

    Raises:
        ValidationError: Si el contenedor o algún identificador no es válido.
    """
    if dependencies is None:
        return []
    if isinstance(dependencies, (str, bytes)) or not isinstance(dependencies, Sequence):
        raise ValidationError("Las dependencias deben ser una lista de IDs.")
    result: List[str] = []
    seen: set[str] = set()
    for raw_dep in dependencies:
        if not isinstance(raw_dep, str):
            raise ValidationError("Cada ID de dependencia debe ser una cadena.")
        cleaned = raw_dep.strip()
        if not cleaned:
            raise ValidationError("El ID de dependencia no puede estar vacío.")
        if cleaned not in seen:
            seen.add(cleaned)
            result.append(cleaned)
    return result


@dataclass
class Task:  # pylint: disable=too-many-instance-attributes
    """Entidad principal que representa una tarea en el sistema."""

    title: str
    description: str = ""
    priority: Priority = Priority.MEDIA
    status: TaskStatus = TaskStatus.PENDIENTE
    due_date: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=current_timestamp_iso)
    updated_at: str = field(default_factory=current_timestamp_iso)

    def __post_init__(self) -> None:
        """Valida y normaliza todos los campos al instanciar la tarea."""
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValidationError("El identificador de la tarea no puede estar vacío.")
        self.id = self.id.strip()

        if not isinstance(self.title, str):
            raise ValidationError("El título de la tarea debe ser una cadena de texto.")
        cleaned_title = self.title.strip()
        if not cleaned_title:
            raise ValidationError("El título de la tarea es obligatorio.")
        if len(cleaned_title) > MAX_TITLE_LENGTH:
            raise ValidationError(
                f"El título no puede superar los {MAX_TITLE_LENGTH} caracteres."
            )
        self.title = cleaned_title

        if self.description is None:
            self.description = ""
        elif not isinstance(self.description, str):
            raise ValidationError("La descripción debe ser una cadena de texto.")
        else:
            self.description = self.description.strip()

        self.priority = Priority.from_value(self.priority)
        self.status = TaskStatus.from_value(self.status)
        self.due_date = validate_due_date(self.due_date)
        self.tags = normalize_tags(self.tags)
        self.dependencies = normalize_dependencies(self.dependencies)

        if self.id in self.dependencies:
            raise InvalidDependencyError(
                f"La tarea '{self.id}' no puede depender de sí misma."
            )

    def is_overdue(self, reference_date: Optional[date] = None) -> bool:
        """Determina si la tarea está vencida respecto a la fecha de referencia.

        Una tarea se considera vencida si tiene fecha límite anterior a
        `reference_date` y su estado no es `completada`.

        Args:
            reference_date: Fecha de comparación (por defecto `date.today()`).

        Returns:
            True si la tarea está vencida y pendiente/en progreso; False en caso contrario.
        """
        if self.due_date is None or self.status == TaskStatus.COMPLETADA:
            return False
        ref = reference_date or date.today()
        return date.fromisoformat(self.due_date) < ref

    def to_dict(self) -> Dict[str, Any]:
        """Serializa la tarea a un diccionario compatible con JSON.

        Returns:
            Diccionario con los atributos primitivos de la tarea.
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "due_date": self.due_date,
            "tags": list(self.tags),
            "dependencies": list(self.dependencies),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Reconstruye una instancia validada de Task a partir de un diccionario.

        Args:
            data: Diccionario con los datos crudos de la tarea.

        Returns:
            Instancia de Task validada.

        Raises:
            ValidationError: Si el diccionario no contiene una estructura válida.
        """
        if not isinstance(data, dict):
            raise ValidationError("Los datos de la tarea deben ser un objeto JSON.")
        created = str(data.get("created_at") or current_timestamp_iso())
        updated = str(data.get("updated_at") or created)
        return cls(
            id=str(data.get("id") or uuid.uuid4()),
            title=data.get("title", ""),
            description=data.get("description", ""),
            priority=data.get("priority", Priority.MEDIA.value),
            status=data.get("status", TaskStatus.PENDIENTE.value),
            due_date=data.get("due_date"),
            tags=data.get("tags", []),
            dependencies=data.get("dependencies", []),
            created_at=created,
            updated_at=updated,
        )


@dataclass
class TaskSummary:
    """Resumen estadístico del tablero de tareas."""

    total: int
    by_status: Dict[str, int]
    by_priority: Dict[str, int]
    overdue_count: int
    blocked_count: int
    completion_rate: float

    def to_dict(self) -> Dict[str, Any]:
        """Serializa el resumen estadístico a un diccionario JSON.

        Returns:
            Diccionario con las métricas agregadas del tablero.
        """
        return {
            "total": self.total,
            "by_status": dict(self.by_status),
            "by_priority": dict(self.by_priority),
            "overdue_count": self.overdue_count,
            "blocked_count": self.blocked_count,
            "completion_rate": self.completion_rate,
        }
