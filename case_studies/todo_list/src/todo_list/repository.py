"""Capa de persistencia en archivo JSON con tolerancia a fallos y corrupción."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any, List, Optional, Union

from todo_list.models import Task, ValidationError


class JsonTaskRepository:
    """Repositorio de tareas respaldado en un archivo JSON local."""

    def __init__(self, file_path: Union[str, Path]) -> None:
        """Inicializa el repositorio asegurando la ruta del archivo JSON.

        Args:
            file_path: Ruta al archivo JSON de almacenamiento.
        """
        self._file_path: Path = Path(file_path)
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        self.corrupted_recoveries: int = 0

    @property
    def file_path(self) -> Path:
        """Retorna la ruta del archivo JSON configurado."""
        return self._file_path

    def list_all(self) -> List[Task]:
        """Carga y retorna todas las tareas almacenadas en el archivo JSON.

        Si el archivo no existe o está vacío, retorna una lista vacía.
        Si el archivo contiene JSON corrupto o estructura inválida, crea una
        copia de seguridad `.corrupt`, reinicia el archivo con `[]` y retorna
        una lista vacía.

        Returns:
            Lista de instancias Task válidas.
        """
        if not self._file_path.exists():
            return []

        try:
            raw_content = self._file_path.read_text(encoding="utf-8").strip()
        except OSError:
            return []

        if not raw_content:
            return []

        try:
            parsed: Any = json.loads(raw_content)
            raw_items = self._extract_items(parsed)
            tasks: List[Task] = [Task.from_dict(item) for item in raw_items]
            return tasks
        except (json.JSONDecodeError, ValidationError, TypeError, ValueError):
            self._handle_corrupted_file()
            return []

    def get_by_id(self, task_id: str) -> Optional[Task]:
        """Busca una tarea por su identificador único.

        Args:
            task_id: Identificador de la tarea a consultar.

        Returns:
            La instancia Task si existe, o None en caso contrario.
        """
        for task in self.list_all():
            if task.id == task_id:
                return task
        return None

    def save_all(self, tasks: List[Task]) -> None:
        """Persiste la colección completa de tareas de forma atómica.

        Args:
            tasks: Lista de tareas a guardar en disco.
        """
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        serialized = [task.to_dict() for task in tasks]
        temp_path = self._file_path.with_suffix(self._file_path.suffix + ".tmp")
        payload = json.dumps(serialized, ensure_ascii=False, indent=2)
        temp_path.write_text(payload, encoding="utf-8")
        os.replace(temp_path, self._file_path)

    def upsert(self, task: Task) -> Task:
        """Inserta una nueva tarea o actualiza una existente con el mismo ID.

        Args:
            task: Entidad Task a almacenar.

        Returns:
            La tarea almacenada.
        """
        tasks = self.list_all()
        updated = False
        for index, current in enumerate(tasks):
            if current.id == task.id:
                tasks[index] = task
                updated = True
                break
        if not updated:
            tasks.append(task)
        self.save_all(tasks)
        return task

    def delete(self, task_id: str) -> bool:
        """Elimina una tarea por su ID si existe.

        Args:
            task_id: Identificador de la tarea a eliminar.

        Returns:
            True si se eliminó la tarea; False si no existía.
        """
        tasks = self.list_all()
        remaining = [task for task in tasks if task.id != task_id]
        if len(remaining) == len(tasks):
            return False
        self.save_all(remaining)
        return True

    @staticmethod
    def _extract_items(parsed: Any) -> List[ Any]:
        """Extrae la lista de diccionarios desde la raíz del JSON cargado.

        Args:
            parsed: Estructura decodificada desde JSON.

        Returns:
            Lista de objetos de tareas.

        Raises:
            ValidationError: Si la estructura raíz no es lista ni objeto válido.
        """
        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, dict) and isinstance(parsed.get("tasks"), list):
            return parsed["tasks"]
        raise ValidationError("Estructura raíz del archivo JSON no válida.")

    def _handle_corrupted_file(self) -> None:
        """Respalda un archivo JSON corrupto y restablece una colección vacía."""
        self.corrupted_recoveries += 1
        backup_path = self._file_path.with_suffix(self._file_path.suffix + ".corrupt")
        try:
            shutil.copyfile(self._file_path, backup_path)
        except OSError:
            pass
        self.save_all([])
