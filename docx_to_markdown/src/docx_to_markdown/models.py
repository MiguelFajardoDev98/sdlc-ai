"""Modelos de datos y esquemas tipados para el convertidor DOCX a Markdown."""

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List


class ElementType(Enum):
    """Tipos de elementos semánticos extraídos de un documento DOCX."""

    HEADING = auto()
    PARAGRAPH = auto()
    LIST_ITEM = auto()
    TABLE = auto()
    IMAGE = auto()
    FOOTNOTE = auto()
    UNSUPPORTED = auto()


@dataclass(frozen=True)
class ConversionConfig:
    """Configuración de parámetros de conversión y guardarraíles."""

    extract_images: bool = True
    assets_dir_name: str = "assets"
    table_cell_linebreak_replacement: str = "<br>"
    emit_manifest: bool = True
    ignore_empty_paragraphs: bool = True


@dataclass
class ElementStats:
    """Métricas cuantitativas de elementos parseados."""

    paragraphs: int = 0
    headings_by_level: Dict[int, int] = field(default_factory=dict)
    tables: int = 0
    table_cells: int = 0
    images: int = 0
    footnotes: int = 0


@dataclass
class ExtractedImage:
    """Representación de imagen binaria extraída del contenedor OOXML."""

    filename: str
    data: bytes
    rel_path: str
    sha256: str
    alt_text: str = ""


@dataclass
class DocumentElement:
    """Elemento atómico extraído del árbol semántico del documento."""

    element_type: ElementType
    content: Any
    level: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversionResult:
    """Resultado final del proceso de conversión y trazabilidad."""

    source_path: Path
    output_path: Path
    stats: ElementStats
    warnings: List[str]
    duration_ms: float
    success: bool
